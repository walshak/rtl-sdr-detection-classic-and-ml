
from flask import Flask, request, jsonify, render_template
import sqlite3
import numpy as np
import math
import os

app = Flask(__name__)
# Always use data folder for database
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DB_PATH = os.getenv('DB_PATH', os.path.join(DATA_DIR, 'detections.db'))

# Chart data processing functions
def process_chart_data(detections, chart_type):
    """Process detections data for specific chart types."""
    if not detections:
        return []
    
    if chart_type == 'time_series':
        return [{
            'timestamp': d.get('timestamp'),
            'peak_power': d.get('peak_power', 0),
            'snr': d.get('snr', 0),
            'bandwidth': d.get('bandwidth', 0),
            'confidence_score': d.get('confidence_score', 0),
            'signal_quality_index': d.get('signal_quality_index', 0),
            'activity_score': d.get('activity_score', 0),
            'label': d.get('label', 'Unknown')
        } for d in detections]
    
    elif chart_type == 'frequency_analysis':
        return [{
            'freq': d.get('freq', 0) / 1e6,  # MHz
            'label': d.get('label', 'Unknown'),
            'peak_power': d.get('peak_power', 0),
            'bandwidth': d.get('bandwidth', 0),
            'spectral_centroid': d.get('spectral_centroid', 0),
            'dominant_frequency': d.get('dominant_frequency', 0),
            'frequency_stability': d.get('frequency_stability', 0),
            'count': 1
        } for d in detections]
    
    elif chart_type == 'signal_quality':
        return [{
            'timestamp': d.get('timestamp'),
            'label': d.get('label', 'Unknown'),
            'snr': d.get('snr', 0),
            'signal_quality_index': d.get('signal_quality_index', 0),
            'confidence_score': d.get('confidence_score', 0),
            'interference_level': d.get('interference_level', 0),
            'baseline_deviation': d.get('baseline_deviation', 0)
        } for d in detections]
    
    elif chart_type == 'advanced_spectral':
        return [{
            'freq': d.get('freq', 0) / 1e6,
            'spectral_centroid': d.get('spectral_centroid', 0),
            'spectral_rolloff': d.get('spectral_rolloff', 0),
            'spectral_flux': d.get('spectral_flux', 0),
            'bandwidth_efficiency': d.get('bandwidth_efficiency', 0),
            'peak_frequencies': decode_peak_frequencies(d.get('peak_frequencies')),
            'label': d.get('label', 'Unknown')
        } for d in detections]
    
    elif chart_type == 'modulation_analysis':
        return [{
            'label': d.get('label', 'Unknown'),
            'timestamp': d.get('timestamp'),
            'modulation_index': d.get('modulation_index', 0),
            'phase_variance': d.get('phase_variance', 0),
            'amplitude_variance': d.get('amplitude_variance', 0),
            'zero_crossing_rate': d.get('zero_crossing_rate', 0)
        } for d in detections]
    
    elif chart_type == 'performance_metrics':
        return [{
            'timestamp': d.get('timestamp'),
            'scan_number': d.get('scan_number', 0),
            'detection_sequence': d.get('detection_sequence', 0),
            'signal_duration': d.get('signal_duration', 0),
            'doppler_shift': d.get('doppler_shift', 0),
            'device_label': d.get('device_label', 'Unknown')
        } for d in detections]
    
    elif chart_type == 'constellation':
        return [{
            'id': d.get('id'),
            'label': d.get('label', 'Unknown'),
            'timestamp': d.get('timestamp'),
            'i': decode_raw_samples_i(d.get('raw_samples')),
            'q': decode_raw_samples_q(d.get('raw_samples')),
            'freq': d.get('freq', 0) / 1e6
        } for d in detections]
    
    elif chart_type in ['spectrum', 'peaks']:
        return [{
            'id': d.get('id'),
            'label': d.get('label', 'Unknown'),
            'timestamp': d.get('timestamp'),
            'freq': d.get('freq', 0) / 1e6,
            'power_spectrum': decode_power_spectrum(d.get('power_spectrum')),
            'peak_power': d.get('peak_power', 0),
            'noise_floor': d.get('noise_floor', 0)
        } for d in detections]
    
    elif chart_type == 'waterfall':
        return [{
            'id': d.get('id'),
            'label': d.get('label', 'Unknown'),
            'timestamp': d.get('timestamp'),
            'freq': d.get('freq', 0) / 1e6,
            'waterfall_data': d.get('waterfall_data', [])
        } for d in detections]
    
    return detections

def decode_peak_frequencies(peak_freq_blob):
    """Decode peak frequencies from binary data."""
    if not peak_freq_blob:
        return []
    try:
        return np.frombuffer(peak_freq_blob, dtype=np.float32).tolist()
    except:
        return []

def decode_raw_samples_i(raw_samples_blob):
    """Decode I component from raw samples binary data."""
    if not raw_samples_blob:
        return []
    try:
        arr = np.frombuffer(raw_samples_blob, dtype=np.complex64)
        return arr.real.tolist()
    except:
        return []

def decode_raw_samples_q(raw_samples_blob):
    """Decode Q component from raw samples binary data."""
    if not raw_samples_blob:
        return []
    try:
        arr = np.frombuffer(raw_samples_blob, dtype=np.complex64)
        return arr.imag.tolist()
    except:
        return []

def decode_power_spectrum(power_spectrum_blob):
    """Decode power spectrum from binary data."""
    if not power_spectrum_blob:
        return []
    try:
        return np.frombuffer(power_spectrum_blob, dtype=np.float32).tolist()
    except:
        return []

# Helper: fetch unique devices
def fetch_devices():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT device_label, device_lat, device_long FROM detections")
    devices = [
        {"device_label": row[0], "device_lat": row[1], "device_long": row[2]}
        for row in c.fetchall()
    ]
    conn.close()
    return devices

@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify(fetch_devices())

# Helper: fetch unique signal labels
def fetch_signal_labels():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT label, COUNT(*) as count FROM detections GROUP BY label ORDER BY count DESC")
    labels = [
        {"label": row[0], "count": row[1]}
        for row in c.fetchall()
    ]
    conn.close()
    return labels

@app.route('/signal_labels', methods=['GET'])
def get_signal_labels():
    """Get list of all unique signal labels in the database with their counts."""
    return jsonify(fetch_signal_labels())

# Helper: fetch detections with search, sort, filter, pagination
def fetch_detections(params):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Build query
    query = "SELECT * FROM detections WHERE 1=1"
    args = []
    # Filtering
    if 'device_label' in params:
        query += " AND device_label = ?"
        args.append(params['device_label'])
    if 'label' in params:
        query += " AND label = ?"
        args.append(params['label'])
    # Support multiple labels (comma-separated)
    if 'labels' in params:
        labels_list = [l.strip() for l in params['labels'].split(',')]
        placeholders = ','.join(['?' for _ in labels_list])
        query += f" AND label IN ({placeholders})"
        args.extend(labels_list)
    if 'min_freq' in params:
        query += " AND freq >= ?"
        args.append(float(params['min_freq']))
    if 'max_freq' in params:
        query += " AND freq <= ?"
        args.append(float(params['max_freq']))
    # Search (by label substring)
    if 'search' in params:
        query += " AND label LIKE ?"
        args.append(f"%{params['search']}%")
    
    # Get total count before pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    c.execute(count_query, args)
    total_count = c.fetchone()[0]
    
    # Sorting
    sort = params.get('sort', 'timestamp')
    order = params.get('order', 'desc')
    if sort not in {'timestamp','freq','label','bandwidth','peak_power','snr'}:
        sort = 'timestamp'
    if order not in {'asc','desc'}:
        order = 'desc'
    query += f" ORDER BY {sort} {order}"
    # Pagination
    page = int(params.get('page', 1))
    
    # Support 'limit' parameter (alias for page_size)
    if 'limit' in params:
        page_size = min(int(params['limit']), 1000)  # Max 1000 items per page
    elif 'page_size' in params:
        page_size = int(params['page_size'])
    else:
        # Default page_size based on chart type
        chart_type = params.get('chart', 'spectrum')
        if chart_type in ['spectrum', 'histogram']:
            page_size = 5
        elif chart_type in ['scatter', 'timeline', 'signal_strength', 'frequency_distribution', 'signal_quality']:
            page_size = 50
        else:
            page_size = 20
    
    # Limit page_size for performance
    chart_type = params.get('chart', 'spectrum')
    if chart_type in ['spectrum', 'histogram']:
        page_size = min(page_size, 10)
    elif chart_type in ['scatter', 'timeline', 'signal_strength', 'frequency_distribution', 'signal_quality']:
        page_size = min(page_size, 200)
    else:
        page_size = min(page_size, 100)
    
    offset = (page - 1) * page_size
    query += " LIMIT ? OFFSET ?"
    args.extend([page_size, offset])
    # Execute
    c.execute(query, args)
    rows = c.fetchall()
    # Format for charting
    detections = []
    for row in rows:
        det = dict(row)
        # Convert fft_history for waterfall charts if present
        if det.get('fft_history'):
            try:
                arr = np.frombuffer(det['fft_history'], dtype=np.float32)
                # Reshape waterfall data (time x frequency)
                nfreq = 512  # Downsampled frequency bins
                ntime = len(arr) // nfreq if len(arr) >= nfreq else 0
                if ntime > 0:
                    det['waterfall_data'] = arr[:ntime*nfreq].reshape((ntime, nfreq)).tolist()
                else:
                    det['waterfall_data'] = []
            except:
                det['waterfall_data'] = []
        else:
            det['waterfall_data'] = []
        detections.append(det)
    conn.close()
    return detections, total_count, page, page_size

@app.route('/detections', methods=['GET'])
def get_detections():
    params = request.args.to_dict()
    detections, total, page, limit = fetch_detections(params)
    # Format for charting: group by chart type
    chart_type = params.get('chart', 'spectrum')
    if chart_type == 'spectrum':
        # Use stored power spectrum data
        data = []
        for d in detections:
            spectrum = []
            if d.get('power_spectrum'):
                try:
                    spectrum = np.frombuffer(d['power_spectrum'], dtype=np.float32).tolist()
                except:
                    spectrum = []
            elif d.get('waterfall_data'):
                # Fallback to waterfall data
                waterfall = d.get('waterfall_data', [])
                spectrum = waterfall[-1] if waterfall else []
            
            data.append({
                'id': d['id'],
                'freq': d['freq'],
                'label': d['label'],
                'timestamp': d['timestamp'],
                'power_spectrum': spectrum,
                'peak_power': d['peak_power'],
                'snr': d['snr'],
                'bandwidth': d['bandwidth']
            })
    elif chart_type == 'histogram':
        data = []
        for d in detections:
            hist = []
            if d.get('power_spectrum'):
                try:
                    spectrum = np.frombuffer(d['power_spectrum'], dtype=np.float32)
                    hist = np.histogram(spectrum, bins=50)[0].tolist()
                except:
                    hist = []
            data.append({
                'id': d['id'],
                'label': d['label'],
                'hist': hist,
                'bins': 50,
                'timestamp': d['timestamp']
            })
    elif chart_type == 'statistics':
        # Statistical analysis chart
        data = [
            {
                'id': d['id'],
                'freq': d['freq'],
                'label': d['label'],
                'timestamp': d['timestamp'],
                'stats': {
                    'mean': d['mean_power'],
                    'std': d['std_power'],
                    'min': d['min_power'],
                    'max': d['max_power'],
                    'peak': d['peak_power'],
                    'noise_floor': d['noise_floor'],
                    'snr': d['snr'],
                    'kurtosis': d['kurtosis'],
                    'skewness': d['skewness'],
                    'num_peaks': d['num_peaks']
                }
            } for d in detections
        ]
    elif chart_type == 'quality':
        # Enhanced signal quality metrics with new fields
        data = [
            {
                'id': d['id'],
                'freq': d['freq'],
                'label': d['label'],
                'timestamp': d['timestamp'],
                'quality_score': d.get('signal_quality_index', min(100, max(0, (d['snr'] or 0) * 2))),
                'confidence_score': d.get('confidence_score', 0),
                'snr': d['snr'],
                'bandwidth': d['bandwidth'],
                'peak_power': d['peak_power'],
                'std_power': d['std_power'],
                'interference_level': d.get('interference_level', 0),
                'baseline_deviation': d.get('baseline_deviation', 0),
                'bandwidth_efficiency': d.get('bandwidth_efficiency', 0)
            } for d in detections
        ]
    elif chart_type == 'features':
        data = [
            {
                'id': d['id'],
                'freq': d['freq'],
                'label': d['label'],
                'timestamp': d['timestamp'],
                'bandwidth': d['bandwidth'],
                'peak_power': d['peak_power'],
                'snr': d['snr'],
                'noise_floor': d['noise_floor'],
                'mean_power': d['mean_power'],
                'std_power': d['std_power'],
                'min_power': d['min_power'],
                'max_power': d['max_power'],
                'kurtosis': d['kurtosis'],
                'skewness': d['skewness'],
                'num_peaks': d['num_peaks']
            } for d in detections
        ]
    elif chart_type == 'waterfall':
        # Waterfall: use pre-processed waterfall data
        data = []
        for d in detections:
            data.append({
                'id': d['id'],
                'freq': d['freq']/1e6,  # MHz
                'label': d['label'],
                'waterfall': d.get('waterfall_data', []),
                'timestamp': d['timestamp']
            })
    elif chart_type == 'timedomain':
        # Time-domain: raw samples (real, imag, magnitude)
        data = []
        for d in detections:
            if d.get('raw_samples'):
                arr = np.frombuffer(d['raw_samples'], dtype=np.complex64)
                real = arr.real.tolist()
                imag = arr.imag.tolist()
                mag = np.abs(arr).tolist()
            else:
                real, imag, mag = [], [], []
            data.append({
                'id': d['id'],
                'label': d['label'],
                'real': real,
                'imag': imag,
                'mag': mag,
                'timestamp': d['timestamp']
            })
    elif chart_type == 'constellation':
        # Constellation: I/Q pairs
        data = []
        for d in detections:
            if d.get('raw_samples'):
                arr = np.frombuffer(d['raw_samples'], dtype=np.complex64)
                i = arr.real.tolist()
                q = arr.imag.tolist()
            else:
                i, q = [], []
            data.append({
                'id': d['id'],
                'label': d['label'],
                'i': i,
                'q': q,
                'timestamp': d['timestamp']
            })
    elif chart_type == 'peaks':
        # Peak detection: spectrum and peak indices
        data = []
        for d in detections:
            if d.get('power_spectrum'):
                arr = np.array(d['power_spectrum'])
                noise_floor = np.median(arr)
                peaks = np.where(arr > noise_floor + 6)[0].tolist()
            else:
                arr, peaks = [], []
            data.append({
                'id': d['id'],
                'label': d['label'],
                'power_spectrum': arr.tolist() if len(arr) else [],
                'peaks': peaks,
                'timestamp': d['timestamp']
            })
    elif chart_type == 'scatter':
        # Scatter plot: frequency vs signal strength
        data = [{
            'id': d['id'],
            'freq': d['freq']/1e6,  # MHz
            'label': d['label'],
            'timestamp': d['timestamp'],
            'peak_power': d['peak_power'],
            'snr': d['snr'],
            'bandwidth': d['bandwidth']
        } for d in detections]
    elif chart_type == 'timeline':
        # Timeline: detections over time
        data = [{
            'id': d['id'],
            'freq': d['freq']/1e6,
            'label': d['label'],
            'timestamp': d['timestamp'],
            'peak_power': d['peak_power'],
            'snr': d['snr']
        } for d in detections]
    elif chart_type == 'signal_strength':
        # Signal strength comparison
        data = [{
            'id': d['id'],
            'freq': d['freq']/1e6,
            'label': d['label'],
            'timestamp': d['timestamp'],
            'peak_power': d['peak_power'],
            'noise_floor': d['noise_floor'],
            'snr': d['snr']
        } for d in detections]
    elif chart_type == 'frequency_distribution':
        # Frequency distribution chart
        data = [{
            'id': d['id'],
            'freq': d['freq']/1e6,
            'label': d['label'],
            'count': 1  # Will be aggregated on frontend
        } for d in detections]
    elif chart_type == 'signal_quality':
        # Signal quality metrics
        data = [{
            'id': d['id'],
            'freq': d['freq']/1e6,
            'label': d['label'],
            'timestamp': d['timestamp'],
            'snr': d['snr'],
            'kurtosis': d['kurtosis'],
            'skewness': d['skewness'],
            'std_power': d['std_power']
        } for d in detections]
    else:
        # Default: return essential fields for dashboard table
        data = [
            {
                'id': d['id'],
                'freq': d['freq'],
                'label': d['label'],
                'timestamp': d['timestamp'],
                'bandwidth': d['bandwidth'],
                'peak_power': d['peak_power'],
                'snr': d['snr'],
                'noise_floor': d['noise_floor'],
                'mean_power': d['mean_power'],
                'std_power': d['std_power'],
                'num_peaks': d['num_peaks'],
                'kurtosis': d['kurtosis'],
                'skewness': d['skewness'],
                'waterfall_data': d.get('waterfall_data', [])
            } for d in detections
        ]
    return jsonify({
        'results': data,
        'count': len(data),
        'total': total,
        'page': page,
        'limit': limit
    })

@app.route('/detections/<int:det_id>', methods=['DELETE'])
def delete_detection(det_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM detections WHERE id = ?', (det_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted', 'id': det_id})

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive statistics for dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Basic counts
    c.execute('SELECT COUNT(*) as total_detections FROM detections')
    total = c.fetchone()['total_detections']
    
    c.execute('SELECT COUNT(DISTINCT device_label) as device_count FROM detections')
    devices = c.fetchone()['device_count']
    
    c.execute('SELECT COUNT(DISTINCT label) as signal_types FROM detections')
    signal_types = c.fetchone()['signal_types']
    
    # Recent activity (last 24 hours)
    c.execute("SELECT COUNT(*) as recent FROM detections WHERE datetime(timestamp) > datetime('now', '-24 hours')")
    recent = c.fetchone()['recent']
    
    # Quality metrics
    c.execute('SELECT AVG(snr) as avg_snr, AVG(signal_quality_index) as avg_quality FROM detections WHERE snr IS NOT NULL')
    quality = c.fetchone()
    
    # Frequency distribution
    c.execute('SELECT label, COUNT(*) as count FROM detections GROUP BY label ORDER BY count DESC LIMIT 10')
    freq_dist = [dict(row) for row in c.fetchall()]
    
    # Time distribution (hourly)
    c.execute("SELECT strftime('%H', timestamp) as hour, COUNT(*) as count FROM detections GROUP BY hour ORDER BY hour")
    hourly = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'summary': {
            'total_detections': total,
            'device_count': devices,
            'signal_types': signal_types,
            'recent_24h': recent,
            'avg_snr': round(quality['avg_snr'] or 0, 2),
            'avg_quality': round(quality['avg_quality'] or 0, 2)
        },
        'frequency_distribution': freq_dist,
        'hourly_activity': hourly
    })

@app.route('/chart_data/<chart_type>', methods=['GET'])
def get_chart_data(chart_type):
    """Get data specifically formatted for different chart types."""
    params = request.args.to_dict()
    
    # Set appropriate page sizes for different chart types
    chart_page_sizes = {
        'spectrum': 5,
        'waterfall': 3,
        'histogram': 10,
        'time_series': 100,
        'frequency_analysis': 200,
        'signal_quality': 100,
        'scatter': 500,
        'heatmap': 1000
    }
    
    params['page_size'] = chart_page_sizes.get(chart_type, 50)
    detections, total, page, limit = fetch_detections(params)
    
    # Process data based on chart type
    if chart_type in ['time_series', 'frequency_analysis', 'signal_quality', 'advanced_spectral', 'modulation_analysis', 'performance_metrics', 'constellation', 'peaks', 'spectrum', 'waterfall', 'histogram', 'scatter', 'timeline', 'signal_strength', 'frequency_distribution']:
        data = process_chart_data([dict(d) for d in detections], chart_type)
    else:
        # Use existing processing with proper serialization
        params['chart'] = chart_type
        raw_data, total, page, limit = fetch_detections(params)
        # Convert any bytes objects to serializable format
        data = []
        for item in raw_data:
            serializable_item = {}
            for key, value in item.items():
                if isinstance(value, bytes):
                    # Skip bytes fields or convert them appropriately
                    continue
                else:
                    serializable_item[key] = value
            data.append(serializable_item)
    
    return jsonify({
        'results': data,
        'count': len(data),
        'total': total,
        'page': page,
        'limit': limit,
        'chart_type': chart_type
    })



# HTML page with Chart.js for interactive charting
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Health check endpoint for Docker
@app.route('/health')
def health_check():
    """Health check endpoint for container monitoring."""
    try:
        # Check database connectivity
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'service': 'rtl-sdr-api'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'rtl-sdr-api'
        }), 503

if __name__ == '__main__':
    app.run(debug=True)
