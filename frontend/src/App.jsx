import { useState, useEffect } from 'react'

function App() {
  const [tests, setTests] = useState([
    { name: 'Backend Server', url: 'http://localhost:8000/', status: 'pending' },
    { name: 'Health Check', url: 'http://localhost:8000/api/health', status: 'pending' },
    { name: 'Stats', url: 'http://localhost:8000/api/stats', status: 'pending' },
  ])

  useEffect(() => {
    runTests()
  }, [])

  const runTests = async () => {
    for (let i = 0; i < tests.length; i++) {
      try {
        const response = await fetch(tests[i].url)
        const data = await response.json()
        
        setTests(prev => prev.map((test, idx) => 
          idx === i ? { ...test, status: 'success', data } : test
        ))
      } catch (error) {
        setTests(prev => prev.map((test, idx) => 
          idx === i ? { ...test, status: 'error', error: error.message } : test
        ))
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
          🏥 Backend Connection Test
        </h1>

        <div className="space-y-4">
          {tests.map((test, index) => (
            <div
              key={index}
              className={`bg-white rounded-lg shadow-md p-6 border-2 ${
                test.status === 'success' ? 'border-green-400' :
                test.status === 'error' ? 'border-red-400' :
                'border-yellow-400'
              }`}
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">
                  {test.status === 'success' ? '✅' :
                   test.status === 'error' ? '❌' : '⏳'}
                </span>
                <h3 className="text-xl font-semibold">{test.name}</h3>
              </div>

              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">URL: </span>
                <span className="bg-gray-100 px-2 py-1 rounded text-xs font-mono">
                  {test.url}
                </span>
              </p>

              {test.status === 'success' && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-gray-700 mb-1">Response:</p>
                  <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40 font-mono">
                    {JSON.stringify(test.data, null, 2)}
                  </pre>
                </div>
              )}

              {test.status === 'error' && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-red-700 mb-1">Error:</p>
                  <p className="text-sm text-red-600">{test.error}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={runTests}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md"
          >
            🔄 Run Tests Again
          </button>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">📡 Connection Info</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Backend URL:</p>
              <div className="mt-1 bg-gray-100 px-3 py-2 rounded font-mono text-xs">
                http://localhost:8000
              </div>
            </div>
            <div>
              <p className="text-gray-600">Frontend URL:</p>
              <div className="mt-1 bg-gray-100 px-3 py-2 rounded font-mono text-xs">
                {window.location.origin}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
