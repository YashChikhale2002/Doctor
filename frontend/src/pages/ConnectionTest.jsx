/**
 * Advanced Connection Testing Component
 * Tests all backend endpoints and displays real-time status
 */

import { useState, useEffect } from 'react';
import { apiService } from '@/services/api.service';
import { ENDPOINTS } from '@/config/api.config';

export default function ConnectionTest() {
  const [tests, setTests] = useState([
    { name: 'Backend Server', endpoint: '/', status: 'pending', duration: null, data: null },
    { name: 'Health Check', endpoint: ENDPOINTS.HEALTH.CHECK, status: 'pending', duration: null, data: null },
    { name: 'Database Stats', endpoint: ENDPOINTS.HEALTH.STATS, status: 'pending', duration: null, data: null },
    { name: 'Ping Test', endpoint: ENDPOINTS.HEALTH.PING, status: 'pending', duration: null, data: null },
  ]);

  const [overallStatus, setOverallStatus] = useState('Testing...');

  useEffect(() => {
    runAllTests();
  }, []);

  const runAllTests = async () => {
    const results = [];

    for (let i = 0; i < tests.length; i++) {
      const test = tests[i];
      const startTime = Date.now();

      try {
        const response = await apiService.get(test.endpoint);
        const duration = Date.now() - startTime;

        results.push({
          ...test,
          status: 'success',
          duration,
          data: response,
        });

        setTests([...results, ...tests.slice(i + 1)]);
      } catch (error) {
        const duration = Date.now() - startTime;

        results.push({
          ...test,
          status: 'error',
          duration,
          data: { error: error.message },
        });

        setTests([...results, ...tests.slice(i + 1)]);
      }

      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    // Check overall status
    const allSuccess = results.every(r => r.status === 'success');
    setOverallStatus(allSuccess ? 'All tests passed! ✅' : 'Some tests failed ❌');
  };

  const retryTest = async (index) => {
    const test = tests[index];
    const startTime = Date.now();

    setTests(tests.map((t, i) => i === index ? { ...t, status: 'pending' } : t));

    try {
      const response = await apiService.get(test.endpoint);
      const duration = Date.now() - startTime;

      setTests(tests.map((t, i) => 
        i === index 
          ? { ...t, status: 'success', duration, data: response }
          : t
      ));
    } catch (error) {
      const duration = Date.now() - startTime;

      setTests(tests.map((t, i) => 
        i === index 
          ? { ...t, status: 'error', duration, data: { error: error.message } }
          : t
      ));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800 border-green-300';
      case 'error': return 'bg-red-100 text-red-800 border-red-300';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'pending': return '⏳';
      default: return '⚪';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🏥 Backend Connection Test
          </h1>
          <p className="text-lg text-gray-600">
            Testing connectivity to Healthcare Platform API
          </p>
          <div className="mt-4 inline-block px-6 py-3 bg-white rounded-lg shadow-md">
            <p className="text-xl font-semibold text-gray-800">{overallStatus}</p>
          </div>
        </div>

        {/* Test Results */}
        <div className="space-y-4">
          {tests.map((test, index) => (
            <div
              key={index}
              className={`bg-white rounded-lg shadow-md border-2 p-6 transition-all duration-300 ${getStatusColor(test.status)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getStatusIcon(test.status)}</span>
                    <h3 className="text-xl font-semibold text-gray-900">{test.name}</h3>
                  </div>

                  <div className="space-y-2 text-sm">
                    <p className="text-gray-700">
                      <span className="font-medium">Endpoint:</span>{' '}
                      de className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {test.endpoint}
                      </code>
                    </p>

                    {test.duration !== null && (
                      <p className="text-gray-700">
                        <span className="font-medium">Duration:</span>{' '}
                        <span className="font-mono">{test.duration}ms</span>
                      </p>
                    )}

                    {test.status === 'success' && test.data && (
                      <div className="mt-3">
                        <p className="font-medium text-gray-700 mb-1">Response:</p>
                        <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto max-h-40">
                          {JSON.stringify(test.data, null, 2)}
                        </pre>
                      </div>
                    )}

                    {test.status === 'error' && test.data && (
                      <div className="mt-3">
                        <p className="font-medium text-red-700 mb-1">Error:</p>
                        <pre className="bg-red-50 p-3 rounded text-xs overflow-x-auto">
                          {JSON.stringify(test.data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>

                {test.status === 'error' && (
                  <button
                    onClick={() => retryTest(index)}
                    className="ml-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                  >
                    Retry
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={runAllTests}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md"
          >
            🔄 Run All Tests Again
          </button>
          
          <a
            href="/dashboard"
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium shadow-md"
          >
            ✅ Go to Dashboard
          </a>
        </div>

        {/* Connection Info */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📡 Connection Info</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Backend URL:</p>
              de className="block mt-1 bg-gray-100 px-3 py-2 rounded text-xs">
                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
              </code>
            </div>
            <div>
              <p className="text-gray-600">Frontend URL:</p>
              de className="block mt-1 bg-gray-100 px-3 py-2 rounded text-xs">
                {window.location.origin}
              </code>
            </div>
            <div>
              <p className="text-gray-600">Environment:</p>
              de className="block mt-1 bg-gray-100 px-3 py-2 rounded text-xs">
                {import.meta.env.MODE}
              </code>
            </div>
            <div>
              <p className="text-gray-600">CORS Status:</p>
              de className="block mt-1 bg-gray-100 px-3 py-2 rounded text-xs">
                {tests.some(t => t.status === 'success') ? '✅ Enabled' : '❌ Check Config'}
              </code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
