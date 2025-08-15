import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import InfrastructureDesigner from './pages/InfrastructureDesigner';
import Observability from './pages/Observability';
import Deployments from './pages/Deployments';
import Costs from './pages/Costs';
import Settings from './pages/Settings';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { AuthProvider } from './contexts/AuthContext';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WebSocketProvider>
          <Router>
            <div className="flex h-screen bg-gray-100">
              <Sidebar />
              <div className="flex-1 flex flex-col overflow-hidden">
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/infrastructure" element={<InfrastructureDesigner />} />
                    <Route path="/observability" element={<Observability />} />
                    <Route path="/deployments" element={<Deployments />} />
                    <Route path="/costs" element={<Costs />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </main>
              </div>
            </div>
            <Toaster position="top-right" />
          </Router>
        </WebSocketProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
