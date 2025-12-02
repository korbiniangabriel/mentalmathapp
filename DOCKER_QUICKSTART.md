# Docker Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Start the App
```bash
./docker-start.sh
```

Or manually:
```bash
docker-compose up -d
```

### Step 2: Access the App
Open your browser to:
```
http://localhost:8501
```

### Step 3: Stop the App
```bash
./docker-stop.sh
```

Or manually:
```bash
docker-compose down
```

## 📋 Common Commands

### View Logs
```bash
docker-compose logs -f
```

### Restart the App
```bash
docker-compose restart
```

### Check Status
```bash
docker-compose ps
```

### Rebuild After Changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access Container Shell
```bash
docker-compose exec mentalmath bash
```

### Run Tests in Container
```bash
docker-compose exec mentalmath pytest tests/
```

## 🔧 Troubleshooting

### Port Already in Use
Edit `docker-compose.yml` and change:
```yaml
ports:
  - "8502:8501"  # Change 8501 to any available port
```

### Container Won't Start
Check logs:
```bash
docker-compose logs
```

### Reset Everything
```bash
docker-compose down -v
rm -rf data/*.db
docker-compose up -d
```

### Permission Issues
```bash
chmod 755 data/
```

## 📊 Data Persistence

Your progress is saved in the `data/` directory, which is mounted as a volume. This means:
- ✅ Data persists across container restarts
- ✅ Data survives container recreation
- ✅ You can backup data by copying the `data/` folder

## 🌐 Network Isolation

The app runs on its own isolated network (`mentalmath-network`), which:
- ✅ Prevents port conflicts with other containers
- ✅ Provides network-level isolation
- ✅ Allows custom DNS resolution
- ✅ Enables easy service discovery

## 🔒 Resource Limits

Default limits (configurable in `docker-compose.yml`):
- CPU: 1 core max, 0.25 cores reserved
- Memory: 512MB max, 128MB reserved

## 📚 Full Documentation

See [DOCKER.md](DOCKER.md) for comprehensive documentation including:
- Development mode
- Security considerations
- Multi-container deployment
- Backup and restore procedures
- Advanced configuration options

## 💡 Pro Tips

1. **First Run**: The first build will take a few minutes. Subsequent starts are instant.

2. **Development**: Uncomment volume mounts in `docker-compose.yml` for live code reloading.

3. **Multiple Instances**: Change the container name and port to run multiple instances.

4. **Monitoring**: Use `docker stats mentalmath-app` to monitor resource usage.

5. **Updates**: Pull new code and run `docker-compose up -d --build` to update.

## 🆘 Need Help?

1. Check logs: `docker-compose logs -f`
2. Read [DOCKER.md](DOCKER.md) for detailed troubleshooting
3. Verify Docker is running: `docker ps`
4. Check Docker version: `docker --version && docker-compose --version`
