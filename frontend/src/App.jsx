import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          🚀 Geko Frontend
        </h1>
        <p className="text-gray-600 mb-6">
          Frontend React + Vite + TailwindCSS configurato correttamente!
        </p>
        <button
          onClick={() => setCount(count + 1)}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Contatore: {count}
        </button>
      </div>
    </div>
  )
}

export default App

