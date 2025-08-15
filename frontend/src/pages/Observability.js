import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function Observability() {
  const [metrics, setMetrics] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');

  useEffect(() => {
    fetchObservabilityData();
  }, [selectedTimeRange]);

  const fetchObservabilityData = async () => {
    // Mock data
    setMetrics([
      { time: '00:00', cpu: 45, memory: 60, network: 30, disk: 25 },
      { time: '04:00', cpu: 52, memory: 65, network: 35, disk: 28 },
      { time: '08:00', cpu: 78, memory: 80, network: 55, disk: 35 },
      { time: '12:00', cpu: 85, memory: 85, network: 70, disk: 40 },
      { time: '16:00', cpu: 72, memory: 75, network: 50, disk: 32 },
      { time: '20:00', cpu: 58, memory: 68, network: 40, disk: 30 },
      { time: '24:00', cpu: 45, memory: 60, network: 30, disk: 25 }
    ]);

    setAlerts([
      {
        id: 1,
        severity: 'warning',
        message: 'High CPU usage detected on web-server-01',
        timestamp: '2 minutes ago',
        status: 'active'
      },
      {
        id: 2,
        severity: 'critical',
        message: 'Database connection pool exhausted',
        timestamp: '5 minutes ago',
        status: 'active'
      },
      {
        id: 3,
        severity: 'info',
        message: 'New deployment completed successfully',
        timestamp: '10 minutes ago',
        status: 'resolved'
      }
    ]);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'info':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
      case 'info':
        return <CheckCircleIcon className="h-5 w-5 text-blue-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Observability</h1>
        <p className="text-gray-600">Monitor your infrastructure and applications</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-6">
        <div className="flex space-x-2">
          {['1h', '6h', '24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => setSelectedTimeRange(range)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                selectedTimeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* System Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="cpu" stroke="#3B82F6" strokeWidth={2} name="CPU %" />
              <Line type="monotone" dataKey="memory" stroke="#10B981" strokeWidth={2} name="Memory %" />
              <Line type="monotone" dataKey="network" stroke="#F59E0B" strokeWidth={2} name="Network %" />
              <Line type="monotone" dataKey="disk" stroke="#EF4444" strokeWidth={2} name="Disk %" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Active Alerts</h3>
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                {getSeverityIcon(alert.severity)}
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                  <p className="text-sm text-gray-500">{alert.timestamp}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(alert.severity)}`}>
                  {alert.severity}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Service Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Service Health</h3>
          <div className="space-y-4">
            {[
              { name: 'Web Server', status: 'healthy', uptime: '99.9%' },
              { name: 'Database', status: 'warning', uptime: '98.5%' },
              { name: 'Load Balancer', status: 'healthy', uptime: '99.8%' },
              { name: 'Cache', status: 'healthy', uptime: '99.7%' }
            ].map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{service.name}</p>
                  <p className="text-sm text-gray-500">Uptime: {service.uptime}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  service.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {service.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Error Rates */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Error Rates</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { service: 'Web', errors: 5, requests: 1000 },
              { service: 'API', errors: 12, requests: 2500 },
              { service: 'Database', errors: 2, requests: 800 },
              { service: 'Cache', errors: 8, requests: 1500 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="service" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="errors" fill="#EF4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            <ChartBarIcon className="h-5 w-5 mr-2" />
            View Detailed Metrics
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            Configure Alerts
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
            <CheckCircleIcon className="h-5 w-5 mr-2" />
            Health Check
          </button>
        </div>
      </div>
    </div>
  );
}
