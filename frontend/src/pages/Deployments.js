import React, { useState, useEffect } from 'react';
import {
  RocketLaunchIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

export default function Deployments() {
  const [deployments, setDeployments] = useState([]);
  const [selectedDeployment, setSelectedDeployment] = useState(null);

  useEffect(() => {
    fetchDeployments();
  }, []);

  const fetchDeployments = async () => {
    // Mock deployment data
    setDeployments([
      {
        id: 'deploy-123',
        name: 'web-app-v1.2.3',
        status: 'completed',
        environment: 'production',
        created_at: '2024-01-01T12:00:00Z',
        completed_at: '2024-01-01T12:05:00Z',
        duration: '5m 30s',
        author: 'john.doe',
        commit: 'abc123',
        replicas: 3
      },
      {
        id: 'deploy-124',
        name: 'api-service-v2.1.0',
        status: 'in_progress',
        environment: 'staging',
        created_at: '2024-01-01T12:10:00Z',
        duration: '2m 15s',
        author: 'jane.smith',
        commit: 'def456',
        replicas: 2
      },
      {
        id: 'deploy-125',
        name: 'frontend-v1.1.0',
        status: 'failed',
        environment: 'development',
        created_at: '2024-01-01T11:30:00Z',
        completed_at: '2024-01-01T11:32:00Z',
        duration: '2m 45s',
        author: 'bob.wilson',
        commit: 'ghi789',
        replicas: 1
      }
    ]);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <ClockIcon className="h-5 w-5 text-blue-500" />;
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Deployments</h1>
        <p className="text-gray-600">Manage and monitor your application deployments</p>
      </div>

      {/* Quick Actions */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <RocketLaunchIcon className="h-5 w-5 mr-2" />
            New Deployment
          </button>
          <button className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">
            <ArrowPathIcon className="h-5 w-5 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Deployments List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Deployments</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {deployments.map((deployment) => (
                <div
                  key={deployment.id}
                  className="px-6 py-4 hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelectedDeployment(deployment)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(deployment.status)}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{deployment.name}</h4>
                        <p className="text-sm text-gray-500">
                          {deployment.environment} • {deployment.author} • {deployment.commit}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(deployment.status)}`}>
                        {deployment.status}
                      </span>
                      <p className="text-sm text-gray-500 mt-1">{deployment.duration}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Deployment Details */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Deployment Details</h3>
            </div>
            <div className="p-6">
              {selectedDeployment ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Name</h4>
                    <p className="text-sm text-gray-500">{selectedDeployment.name}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Status</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedDeployment.status)}`}>
                      {selectedDeployment.status}
                    </span>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Environment</h4>
                    <p className="text-sm text-gray-500">{selectedDeployment.environment}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Created</h4>
                    <p className="text-sm text-gray-500">{formatDate(selectedDeployment.created_at)}</p>
                  </div>
                  {selectedDeployment.completed_at && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Completed</h4>
                      <p className="text-sm text-gray-500">{formatDate(selectedDeployment.completed_at)}</p>
                    </div>
                  )}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Duration</h4>
                    <p className="text-sm text-gray-500">{selectedDeployment.duration}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Author</h4>
                    <p className="text-sm text-gray-500">{selectedDeployment.author}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Commit</h4>
                    <p className="text-sm text-gray-500 font-mono">{selectedDeployment.commit}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Replicas</h4>
                    <p className="text-sm text-gray-500">{selectedDeployment.replicas}</p>
                  </div>
                  
                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex space-x-2">
                      <button className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">
                        View Logs
                      </button>
                      {selectedDeployment.status === 'completed' && (
                        <button className="flex-1 px-3 py-2 bg-yellow-600 text-white text-sm rounded-md hover:bg-yellow-700">
                          Rollback
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <RocketLaunchIcon className="h-12 w-12 mx-auto mb-4" />
                  <p>Select a deployment to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Deployment Statistics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Successful</p>
              <p className="text-2xl font-bold text-gray-900">24</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">1</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <RocketLaunchIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">28</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
