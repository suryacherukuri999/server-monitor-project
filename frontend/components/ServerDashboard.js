// components/ServerDashboard.js
import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Server } from 'lucide-react';

const ServerDashboard = () => {
  const [serverStatus, setServerStatus] = useState({});
  const [lastChecked, setLastChecked] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkServers = async () => {
    try {
      console.log('Fetching server status...'); // Debug log
      const response = await fetch('http://localhost:5000/api/status', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received data:', data); // Debug log - check your browser console
      
      setServerStatus(data || {});  // Ensure we set an empty object if data is null
      setLastChecked(new Date().toISOString());
      setError(null);
    } catch (error) {
      console.error('Error fetching status:', error);
      setError('Failed to connect to monitoring server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkServers();
    const interval = setInterval(checkServers, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="text-center">Loading server status...</div>
      </div>
    );
  }

  // Add debug output
  console.log('Current serverStatus:', serverStatus);
  
  const offlineServers = Object.values(serverStatus).filter(s => s?.status === 'offline').length;
  console.log('Number of offline servers:', offlineServers);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Server Status Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last checked: {lastChecked ? new Date(lastChecked).toLocaleString() : 'Never'}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
          {error}
        </div>
      )}

      {offlineServers > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <div className="font-semibold text-red-600">Critical Alert</div>
          </div>
          <div className="mt-1 text-red-600">
            {offlineServers} server{offlineServers > 1 ? 's are' : ' is'} currently offline!
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Debug output */}
        {console.log('Rendering servers:', Object.entries(serverStatus))}
        
        {Object.entries(serverStatus).map(([server, status]) => {
          console.log('Rendering server:', server, status); // Debug output
          return (
            <div 
              key={server}
              className={`p-4 rounded-lg border ${
                status.status === 'online' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <Server className="h-5 w-5" />
                <h2 className="text-lg font-semibold">{server}</h2>
                {status.status === 'online' ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500 ml-auto" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-500 ml-auto" />
                )}
              </div>
              
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className={status.status === 'online' ? 'text-green-600' : 'text-red-600'}>
                    {status.status === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Last Checked:</span>
                  <span>{new Date(status.last_checked).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ServerDashboard;