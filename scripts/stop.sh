#!/bin/bash

# PwrSysPro Analysis Suite - Stop Script
# Stops both backend and frontend servers

echo "🛑 Stopping PwrSysPro Analysis Suite..."

# Read PIDs from files
if [ -f "/tmp/pwrsyspro_backend.pid" ]; then
    BACKEND_PID=$(cat /tmp/pwrsyspro_backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm /tmp/pwrsyspro_backend.pid
        echo "   ✅ Backend stopped"
    else
        echo "   ⚠️  Backend not running"
        rm /tmp/pwrsyspro_backend.pid
    fi
else
    echo "   ⚠️  Backend PID file not found"
fi

if [ -f "/tmp/pwrsyspro_frontend.pid" ]; then
    FRONTEND_PID=$(cat /tmp/pwrsyspro_frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm /tmp/pwrsyspro_frontend.pid
        echo "   ✅ Frontend stopped"
    else
        echo "   ⚠️  Frontend not running"
        rm /tmp/pwrsyspro_frontend.pid
    fi
else
    echo "   ⚠️  Frontend PID file not found"
fi

echo ""
echo "✅ PwrSysPro stopped"
