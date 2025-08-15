import React, { useState, useRef } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import {
  ServerIcon,
  GlobeAltIcon,
  DatabaseIcon,
  CloudIcon,
  TrashIcon,
  PlayIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import Editor from '@monaco-editor/react';

const componentTypes = [
  { type: 'ec2', name: 'EC2 Instance', icon: ServerIcon, color: 'bg-blue-500' },
  { type: 'vpc', name: 'VPC', icon: CloudIcon, color: 'bg-green-500' },
  { type: 'rds', name: 'RDS Database', icon: DatabaseIcon, color: 'bg-purple-500' },
  { type: 'alb', name: 'Load Balancer', icon: GlobeAltIcon, color: 'bg-orange-500' },
  { type: 'lambda', name: 'Lambda Function', icon: CloudIcon, color: 'bg-yellow-500' },
  { type: 's3', name: 'S3 Bucket', icon: DatabaseIcon, color: 'bg-red-500' },
];

const DraggableComponent = ({ component, onDrop }) => {
  const [{ isOver }, drop] = useDrop({
    accept: 'component',
    drop: (item) => onDrop(item, component.id),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  return (
    <div
      ref={drop}
      className={`p-4 border-2 border-dashed rounded-lg ${
        isOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      }`}
    >
      <div className="text-center text-gray-500">
        <CloudIcon className="h-8 w-8 mx-auto mb-2" />
        <p>Drop component here</p>
      </div>
    </div>
  );
};

const ComponentItem = ({ component, onDelete, onConfigure }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'component',
    item: component,
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  const ComponentIcon = component.icon;

  return (
    <div
      ref={drag}
      className={`p-4 border rounded-lg cursor-move ${
        isDragging ? 'opacity-50' : 'opacity-100'
      } bg-white shadow-sm hover:shadow-md transition-shadow`}
    >
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${component.color}`}>
          <ComponentIcon className="h-5 w-5 text-white" />
        </div>
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{component.name}</h4>
          <p className="text-sm text-gray-500">{component.type}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onConfigure(component)}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            <DocumentTextIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onDelete(component.id)}
            className="p-1 text-gray-400 hover:text-red-600"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default function InfrastructureDesigner() {
  const [design, setDesign] = useState({
    name: '',
    environment: 'development',
    cloudProvider: 'aws',
    components: []
  });
  const [showTerraform, setShowTerraform] = useState(false);
  const [terraformCode, setTerraformCode] = useState('');
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [showConfigModal, setShowConfigModal] = useState(false);

  const handleDrop = (item, targetId) => {
    const newComponent = {
      id: Date.now(),
      ...item,
      configuration: {}
    };
    setDesign(prev => ({
      ...prev,
      components: [...prev.components, newComponent]
    }));
  };

  const handleDelete = (componentId) => {
    setDesign(prev => ({
      ...prev,
      components: prev.components.filter(c => c.id !== componentId)
    }));
  };

  const handleConfigure = (component) => {
    setSelectedComponent(component);
    setShowConfigModal(true);
  };

  const handleSaveConfiguration = (configuration) => {
    setDesign(prev => ({
      ...prev,
      components: prev.components.map(c =>
        c.id === selectedComponent.id
          ? { ...c, configuration }
          : c
      )
    }));
    setShowConfigModal(false);
    setSelectedComponent(null);
  };

  const generateTerraform = async () => {
    try {
      const response = await fetch('/api/v1/infrastructure/design', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(design),
      });
      
      const result = await response.json();
      if (result.success) {
        setTerraformCode(result.terraform_code);
        setShowTerraform(true);
      }
    } catch (error) {
      console.error('Failed to generate Terraform:', error);
    }
  };

  const deployInfrastructure = async () => {
    try {
      const response = await fetch('/api/v1/infrastructure/deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(design),
      });
      
      const result = await response.json();
      if (result.success) {
        alert('Infrastructure deployment started!');
      }
    } catch (error) {
      console.error('Failed to deploy infrastructure:', error);
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Infrastructure Designer</h1>
          <p className="text-gray-600">Drag and drop components to design your infrastructure</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Component Palette */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Components</h3>
              <div className="space-y-3">
                {componentTypes.map((component) => (
                  <DraggableComponent
                    key={component.type}
                    component={component}
                    onDrop={handleDrop}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Design Canvas */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Design Canvas</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={generateTerraform}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Generate Terraform
                  </button>
                  <button
                    onClick={deployInfrastructure}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    <PlayIcon className="h-4 w-4 inline mr-2" />
                    Deploy
                  </button>
                </div>
              </div>

              {/* Design Form */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={design.name}
                    onChange={(e) => setDesign(prev => ({ ...prev, name: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Environment</label>
                  <select
                    value={design.environment}
                    onChange={(e) => setDesign(prev => ({ ...prev, environment: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="development">Development</option>
                    <option value="staging">Staging</option>
                    <option value="production">Production</option>
                  </select>
                </div>
              </div>

              {/* Components List */}
              <div className="space-y-3">
                {design.components.map((component) => (
                  <ComponentItem
                    key={component.id}
                    component={component}
                    onDelete={handleDelete}
                    onConfigure={handleConfigure}
                  />
                ))}
                {design.components.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <CloudIcon className="h-12 w-12 mx-auto mb-4" />
                    <p>Drag components from the palette to start designing</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Terraform Preview */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Terraform Preview</h3>
              {showTerraform ? (
                <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-auto">
                  <Editor
                    height="100%"
                    language="hcl"
                    value={terraformCode}
                    theme="vs-dark"
                    options={{
                      readOnly: true,
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                    }}
                  />
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <DocumentTextIcon className="h-12 w-12 mx-auto mb-4" />
                  <p>Generate Terraform to see the code</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Configuration Modal */}
        {showConfigModal && selectedComponent && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Configure {selectedComponent.name}
              </h3>
              <ComponentConfigurationForm
                component={selectedComponent}
                onSave={handleSaveConfiguration}
                onCancel={() => setShowConfigModal(false)}
              />
            </div>
          </div>
        )}
      </div>
    </DndProvider>
  );
}

// Component Configuration Form
function ComponentConfigurationForm({ component, onSave, onCancel }) {
  const [config, setConfig] = useState(component.configuration || {});

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(config);
  };

  const renderConfigFields = () => {
    switch (component.type) {
      case 'ec2':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700">Instance Type</label>
              <select
                value={config.instanceType || 't3.micro'}
                onChange={(e) => setConfig(prev => ({ ...prev, instanceType: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              >
                <option value="t3.micro">t3.micro</option>
                <option value="t3.small">t3.small</option>
                <option value="t3.medium">t3.medium</option>
                <option value="t3.large">t3.large</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Storage (GB)</label>
              <input
                type="number"
                value={config.storage || 20}
                onChange={(e) => setConfig(prev => ({ ...prev, storage: parseInt(e.target.value) }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              />
            </div>
          </>
        );
      case 'rds':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700">Engine</label>
              <select
                value={config.engine || 'mysql'}
                onChange={(e) => setConfig(prev => ({ ...prev, engine: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              >
                <option value="mysql">MySQL</option>
                <option value="postgres">PostgreSQL</option>
                <option value="aurora">Aurora</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Instance Class</label>
              <select
                value={config.instanceClass || 'db.t3.micro'}
                onChange={(e) => setConfig(prev => ({ ...prev, instanceClass: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              >
                <option value="db.t3.micro">db.t3.micro</option>
                <option value="db.t3.small">db.t3.small</option>
                <option value="db.t3.medium">db.t3.medium</option>
              </select>
            </div>
          </>
        );
      default:
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              value={config.name || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, name: e.target.value }))}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
            />
          </div>
        );
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {renderConfigFields()}
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Save
        </button>
      </div>
    </form>
  );
}
