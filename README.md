# server-monitor-project


# server (backend)
1. Install conda and create an environment (use python3 (3.12.4))
2. cd server-monitor-project
3. cd backend
4. pip install -r requirements.txt
5. python server_monitor.py (use nohup for non termination)


# UI (frontend)
1. cd ..
2. cd frontend
3. rm -rf node_modules package-lock.json .next 
4. npm install
5. npm run dev