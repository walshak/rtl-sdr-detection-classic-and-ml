# AeroShield Integration Guide

## What's New?

The RTL-SDR detection system now includes **AeroShield**, a modern Next.js frontend for visualizing RF signal detections.

## Architecture

```
┌─────────────────────┐
│   AeroShield Web    │  Port 3000 (Main Interface)
│   (Next.js)         │
└──────────┬──────────┘
           │
           │ API Calls
           ▼
┌─────────────────────┐
│   Flask API         │  Port 5000 (Backend)
│   (api.py)          │
└──────────┬──────────┘
           │
           │ Database
           ▼
┌─────────────────────┐
│   SQLite DB         │
│   (detections.db)   │
└─────────────────────┘
```

## Services

### 1. AeroShield Frontend (Port 3000)
- Modern React/Next.js interface
- Real-time RF signal visualization
- Interactive maps with Leaflet
- User authentication with JWT
- Material-UI components

### 2. Flask API Backend (Port 5000)
- RESTful API for detections
- Device management
- Signal processing data

### 3. RTL-SDR Listener
- Background service detecting RF signals
- Writes to SQLite database
- Configurable device index

## Access Points

- **Main Dashboard:** http://localhost:3000 (AeroShield)
- **API Endpoint:** http://localhost:5000
- **Database:** `./data/detections.db`

## Environment Variables

### AeroShield (.env in AeroShield folder)
```env
DATABASE_URL=mongodb+srv://...  # MongoDB for user data
JWT_SECRET=aero-shield-secret-key
API_BASE_URL=http://127.0.0.1:5000  # Points to Flask API
```

### RTL-SDR Backend (.env in root)
```env
RTL_SDR_DEVICE=0
DEVICE_LABEL=DEVICE_1
DEVICE_LAT=0.0
DEVICE_LONG=0.0
```

## First Time Setup

1. **Start the system:**
   ```bash
   .\START-RTLSDR.bat
   ```
   (Must run as Administrator)

2. **AeroShield will open automatically** at http://localhost:3000

3. **Login or Register** on the AeroShield interface

4. **View Detections** - The dashboard will show real-time RF signals

## Development Workflow

### Update Frontend (AeroShield)
```bash
cd AeroShield
npm install  # If new dependencies
npm run dev  # Test locally
docker-compose build aeroshield-frontend  # Rebuild container
docker-compose up -d aeroshield-frontend  # Restart
```

### Update Backend (Python)
- Just edit the Python files (listen.py, api.py, etc.)
- Changes are live due to volume mounts
- Restart if needed: `docker-compose restart rtl-sdr-web`

### Update Database
- Changes persist in `./data/detections.db`
- Backed up automatically to `./backups/`

## Troubleshooting

### AeroShield won't start
```bash
# Check logs
docker-compose logs aeroshield-frontend

# Rebuild
docker-compose build aeroshield-frontend
docker-compose up -d aeroshield-frontend
```

### API connection issues
- Ensure Flask backend is running: `docker ps`
- Check API is accessible: http://localhost:5000/detections
- Verify `.env` in AeroShield has correct API_BASE_URL

### Port conflicts
- Port 3000 in use: Edit docker-compose.yml, change `"3000:3000"` to `"3001:3000"`
- Port 5000 in use: Change `"5000:5000"` to `"5001:5000"`

### Build errors
```bash
# Clean build
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

## Container Management

### View all services
```bash
docker-compose ps
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f aeroshield-frontend
docker-compose logs -f rtl-sdr-web
docker-compose logs -f rtl-sdr-listener
```

### Restart specific service
```bash
docker-compose restart aeroshield-frontend
docker-compose restart rtl-sdr-web
```

### Stop everything
```bash
.\STOP-RTLSDR.bat
# or
docker-compose down
```

## Performance Notes

- **First build:** 5-10 minutes (building Next.js app)
- **Subsequent starts:** 10-30 seconds
- **Memory usage:** ~3-5GB (includes Next.js, Flask, Python services)
- **CPU usage:** 15-40% (depending on detection activity)

## Data Flow

1. **RTL-SDR Device** → Detects RF signals
2. **listen.py** → Processes and stores in SQLite
3. **api.py** → Exposes data via REST API
4. **AeroShield** → Fetches and displays data
5. **User** → Interacts with visualizations

---

**Note:** The old dashboard (templates/dashboard.html) is still available at http://localhost:5000 for testing purposes.
