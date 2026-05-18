import os
import threading
import time
import socket
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for
from werkzeug.utils import secure_filename
import mimetypes

from config import config
from models import db, SharedItem

app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)

# Create tables
with app.app_context():
    db.create_all()
    print("✓ Database tables created")

def cleanup_expired_items():
    """Background thread to cleanup expired items"""
    while True:
        with app.app_context():
            try:
                now = datetime.now()
                expired_items = SharedItem.query.filter(
                    SharedItem.expires_at <= now
                ).all()
                
                for item in expired_items:
                    # Delete file if it exists
                    if item.item_type == 'file' and item.file_path:
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], item.file_path)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"Deleted file: {item.file_path}")
                    
                    # Delete from database
                    db.session.delete(item)
                    print(f"Deleted expired item: {item.item_id}")
                
                if expired_items:
                    db.session.commit()
                    print(f"Cleaned up {len(expired_items)} expired items")
                    
            except Exception as e:
                print(f"Cleanup error: {e}")
                db.session.rollback()
        
        time.sleep(3600)  # Run every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_expired_items, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Home page - list all active shares"""
    now = datetime.now()
    active_items = SharedItem.query.filter(
        SharedItem.expires_at > now
    ).order_by(SharedItem.created_at.desc()).all()
    
    return render_template('index.html', items=active_items)

@app.route('/api/items')
def get_items():
    """API endpoint to get all active items"""
    try:
        now = datetime.now()
        active_items = SharedItem.query.filter(
            SharedItem.expires_at > now
        ).order_by(SharedItem.created_at.desc()).all()
        
        return jsonify({
            'items': [item.to_dict() for item in active_items],
            'count': len(active_items)
        })
    except Exception as e:
        print(f"Error in get_items: {e}")
        return jsonify({'items': [], 'count': 0, 'error': str(e)}), 500

@app.route('/share/text', methods=['POST'])
def share_text():
    """Share a text snippet"""
    try:
        data = request.get_json()
        title = data.get('title', 'Untitled Text')
        content = data.get('content', '')
        expiry_option = data.get('expiry', '1_hour')
        
        # Get expiry time in seconds
        expiry_seconds = app.config['DEFAULT_EXPIRY_OPTIONS'].get(expiry_option, 3600)
        
        if not content or not content.strip():
            return jsonify({'error': 'Content is required'}), 400
        
        # Create new text share
        text_item = SharedItem(
            item_type='text',
            expires_in_seconds=expiry_seconds,
            title=title.strip(),
            content=content.strip()
        )
        
        db.session.add(text_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': text_item.to_dict(),
            'share_url': f"/view/{text_item.item_id}"
        })
        
    except Exception as e:
        print(f"Error in share_text: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/share/file', methods=['POST'])
def share_file():
    """Share a file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        expiry_option = request.form.get('expiry', '1_hour')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get expiry time in seconds
        expiry_seconds = app.config['DEFAULT_EXPIRY_OPTIONS'].get(expiry_option, 3600)
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create database entry
        file_item = SharedItem(
            item_type='file',
            expires_in_seconds=expiry_seconds,
            filename=filename,
            file_path=unique_filename,
            file_size=file_size
        )
        
        db.session.add(file_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': file_item.to_dict(),
            'share_url': f"/download/{file_item.item_id}"
        })
        
    except Exception as e:
        print(f"Error in share_file: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/view/<item_id>')
def view_item(item_id):
    """View a shared text item"""
    item = SharedItem.query.filter_by(item_id=item_id).first_or_404()
    
    if item.is_expired():
        return render_template('expired.html'), 410
    
    if item.item_type == 'text':
        return render_template('file_detail.html', item=item)
    else:
        return redirect(url_for('download_file', item_id=item_id))

@app.route('/download/<item_id>')
def download_file(item_id):
    """Download a shared file"""
    item = SharedItem.query.filter_by(item_id=item_id).first_or_404()
    
    if item.is_expired():
        return render_template('expired.html'), 410
    
    if item.item_type != 'file':
        abort(400, description="This is not a file")
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], item.file_path)
    
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    # Increment download count
    item.download_count += 1
    db.session.commit()
    
    # Get mime type
    mime_type = mimetypes.guess_type(item.filename)[0] or 'application/octet-stream'
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=item.filename,
        mimetype=mime_type
    )

@app.route('/api/item/<item_id>/time-remaining')
def get_time_remaining(item_id):
    """Get remaining time for an item (for live updates)"""
    item = SharedItem.query.filter_by(item_id=item_id).first_or_404()
    
    return jsonify({
        'id': item.item_id,
        'time_remaining': item.get_time_remaining(),
        'is_expired': item.is_expired()
    })

@app.route('/api/item/<item_id>/content')
def get_item_content(item_id):
    """Get the content of a text item (for copy functionality)"""
    item = SharedItem.query.filter_by(item_id=item_id).first_or_404()
    
    if item.item_type != 'text':
        return jsonify({'error': 'Not a text item'}), 400
    
    if item.is_expired():
        return jsonify({'error': 'Item expired'}), 410
    
    return jsonify({
        'id': item.item_id,
        'content': item.content
    })

@app.route('/api/network-ip')
def get_network_ip():
    """Get the network IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return jsonify({'ip': ip})
    except Exception:
        return jsonify({'ip': '127.0.0.1'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)