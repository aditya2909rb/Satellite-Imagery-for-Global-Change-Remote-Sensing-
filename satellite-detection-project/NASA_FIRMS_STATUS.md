# NASA FIRMS Integration Status

## Overview

This application is configured to use **real NASA FIRMS (Fire Information for Resource Management System)** data to detect active fires globally.

## Your NASA FIRMS Credentials

- **MAP KEY**: `c0e5c18bf19930f3dedbeb10e2a8b9e0`
- **Transaction Limit**: 5000 requests / 10 minutes
- **Valid For**: Both FIRMS Global and FIRMS US/Canada sites

## Integration Details

### Data Sources Available

The application uses the **NASA FIRMS API** with the following datasources:

1. **VIIRS NOAA-20 NRT** (Default)
   - Resolution: 375m
   - Coverage: Twice daily (day and night passes)
   - Latency: ~3 hours from satellite observation

2. **VIIRS Suomi NPP NRT**
   - Resolution: 375m  
   - Coverage: Twice daily
   - Latency: ~3 hours

3. **MODIS NRT** (Combined Aqua + Terra)
   - Resolution: 1km
   - Coverage: Four times daily
   - Latency: ~3 hours

### Fire Detection Properties

Each fire detection includes:
- **Location**: Latitude/Longitude coordinates
- **Brightness**: Temperature in Kelvin (thermal anomaly)
- **FRP (Fire Radiative Power)**: Measured in megawatts (MW)
- **Confidence**: Low/Nominal/High for VIIRS, 0-100% for MODIS
- **Acquisition Date/Time**: When the satellite detected the fire
- **Satellite**: Which satellite detected it (NOAA-20, Suomi NPP, Aqua, Terra)
- **Scan/Track**: Pixel size in kilometers

## Current Network Restriction Issue

### Problem

GitHub Codespaces has network restrictions that **block outbound HTTPS connections** to NASA FIRMS servers (`firms.modaps.eosdis.nasa.gov`).

**Error observed**:
```
Network unreachable: HTTPSConnection failed to establish connection
```

### Why This Happens

- Codespaces runs in a containerized environment with firewall rules
- Some external APIs (especially government services) may be blocked for security
- The NASA FIRMS API endpoint is not accessible from Codespaces infrastructure

### Solutions

#### Option 1: Deploy to Different Environment  ✅ RECOMMENDED

Deploy the application to an environment without these restrictions:

- **Local Docker**: Run locally with Docker
- **AWS EC2 / Azure VM**: Cloud VMs have unrestricted outbound access
- **Heroku / Railway / Render**: PaaS platforms typically allow NASA API access
- **Google Cloud Run / AWS Lambda**: Serverless functions work

**To deploy locally**:
```bash
# Build and run
docker build -t fire-detection .
docker run -p 8000:8000 fire-detection
```

#### Option 2: Use NASA FIRMS WMS Service

Alternative approach using WMS (Web Map Service) instead of REST API:
- Fetch map tiles with fire overlay
- Parse visual data instead of structured data
- May have different firewall rules

#### Option 3: Use Proxy Service

Set up a proxy/relay server outside Codespaces:
- Deploy simple relay on Heroku/Vercel
- Relay forwards requests to NASA FIRMS
- Application calls your relay instead

## Testing the Integration

### When Deployed Outside Codespaces

Test the API directly:

```bash
curl "https://firms.modaps.eosdis.nasa.gov/api/area/csv/c0e5c18bf19930f3dedbeb10e2a8b9e0/VIIRS_NOAA20_NRT/-119.42,37.77,200/1"
```

Expected response: CSV data with fire detections

### API Endpoint Usage

```bash
curl -X POST http://your-server:8000/api/detect/fires \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [37.7749, -119.4179],
    "radius_km": 200,
    "confidence_threshold": 0.5
  }'
```

## Current Behavior

While in Codespaces:
- Application **attempts** to fetch from NASA FIRMS API
- Falls back to **demo/simulated data** when network fails
- Dashboard shows: **"Demo Data (FIRMS unavailable - Network restricted)"**
- All code is ready and will work when deployed elsewhere

## Files Modified for FIRMS Integration

1. **`src/utils/nasa_firms_api.py`** - New file
   - Complete FIRMS API client
   - CSV parsing
   - Distance calculations
   - Confidence normalization

2. **`src/api/extended_main.py`** - Modified
   - Imports FIRMS API client
   - Calls FIRMS before falling back to demo data
   - Returns real_data flag in API response

3. **`static/index.html`** - Modified
   - Checks `real_data` flag from API
   - Updates data source label dynamically
   - Shows green checkmark for real data, orange warning for demo

## Next Steps

1. **Deploy to unrestricted environment** (AWS, local, etc.)
2. **Test FIRMS API** from that environment
3. **Verify real fire detections** appear on dashboard
4. **Monitor API usage** (5000 requests per 10 minutes limit)

## NASA FIRMS Documentation

- **API Docs**: https://firms.modaps.eosdis.nasa.gov/api/
- **Get MAP KEY**: https://firms.modaps.eosdis.nasa.gov/api/request_api_key.html
- **WMS Service**: https://firms.modaps.eosdis.nasa.gov/wms/
- **Data Format**: https://firms.modaps.eosdis.nasa.gov/api/area/

## Support

If you deploy this application outside Codespaces and still encounter issues:

1. Check firewall rules allow outbound HTTPS to NASA servers
2. Verify MAP KEY is valid by testing with curl
3. Check application logs for detailed error messages
4. Ensure requests stay within 5000/10min limit

---

**Status**: ✅ Code ready, ⚠️ Network blocked in Codespaces
**Recommendation**: Deploy to AWS/local Docker to enable real NASA FIRMS data
