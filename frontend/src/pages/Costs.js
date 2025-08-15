import React, { useState, useEffect } from 'react';
import {
  CurrencyDollarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ExclamationTriangleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Costs() {
  const [costs, setCosts] = useState({});
  const [forecast, setForecast] = useState({});
  const [breakdown, setBreakdown] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('current');

  useEffect(() => {
    fetchCostData();
  }, [selectedPeriod]);

  const fetchCostData = async () => {
    // Mock cost data
    setCosts({
      current_month: 2450.75,
      previous_month: 2200.50,
      change_percentage: 11.4,
      trend: 'increasing'
    });

    setForecast({
      current_month: 2450.75,
      forecast: [
        { month: '2024-02', estimated: 2600.00 },
        { month: '2024-03', estimated: 2750.00 },
        { month: '2024-04', estimated: 2900.00 }
      ],
      trend: 'increasing',
      recommendations: [
        'Consider using reserved instances for predictable workloads',
        'Review and terminate unused EBS volumes',
        'Optimize Lambda function memory allocation'
      ]
    });

    setBreakdown([
      { name: 'EC2', value: 1200.50, color: '#3B82F6' },
      { name: 'RDS', value: 450.25, color: '#10B981' },
      { name: 'S3', value: 150.00, color: '#F59E0B' },
      { name: 'Lambda', value: 200.00, color: '#EF4444' },
      { name: 'ALB', value: 100.00, color: '#8B5CF6' },
      { name: 'CloudWatch', value: 50.00, color: '#06B6D4' },
      { name: 'Other', value: 300.00, color: '#6B7280' }
    ]);
  };

  const getTrendIcon = (trend) => {
    return trend === 'increasing' ? (
      <TrendingUpIcon className="h-5 w-5 text-red-500" />
    ) : (
      <TrendingDownIcon className="h-5 w-5 text-green-500" />
    );
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Cost Management</h1>
        <p className="text-gray-600">Monitor and optimize your cloud spending</p>
      </div>

      {/* Period Selector */}
      <div className="mb-6">
        <div className="flex space-x-2">
          {['current', 'previous', 'forecast'].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                selectedPeriod === period
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {period.charAt(0).toUpperCase() + period.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Cost Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Current Month</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(costs.current_month)}</p>
            </div>
            <div className="p-2 bg-blue-100 rounded-lg">
              <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center">
            {getTrendIcon(costs.trend)}
            <span className={`ml-2 text-sm font-medium ${
              costs.trend === 'increasing' ? 'text-red-600' : 'text-green-600'
            }`}>
              {costs.change_percentage}% from last month
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Previous Month</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(costs.previous_month)}</p>
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Forecast (Next Month)</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(forecast.forecast?.[0]?.estimated || 0)}</p>
            </div>
            <div className="p-2 bg-yellow-100 rounded-lg">
              <TrendingUpIcon className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Cost Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[
              { month: 'Oct', cost: 2000 },
              { month: 'Nov', cost: 2100 },
              { month: 'Dec', cost: 2200 },
              { month: 'Jan', cost: 2450 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Line type="monotone" dataKey="cost" stroke="#3B82F6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={breakdown}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {breakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Service Costs */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Service Costs</h3>
          <div className="space-y-4">
            {breakdown.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: service.color }}
                  />
                  <span className="font-medium text-gray-900">{service.name}</span>
                </div>
                <span className="font-medium text-gray-900">{formatCurrency(service.value)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Optimization Recommendations */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Optimization Recommendations</h3>
          <div className="space-y-4">
            {forecast.recommendations?.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mt-0.5" />
                <p className="text-sm text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            <CurrencyDollarIcon className="h-5 w-5 mr-2" />
            Set Budget Alerts
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
            <TrendingDownIcon className="h-5 w-5 mr-2" />
            Optimize Resources
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700">
            <ChartBarIcon className="h-5 w-5 mr-2" />
            Generate Report
          </button>
        </div>
      </div>
    </div>
  );
}
