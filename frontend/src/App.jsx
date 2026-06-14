import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [started, setStarted] = useState(false)
  const [stats, setStats] = useState({ total_cars: 0 })
  
  // ML & Search Input States
  const [companyName, setCompanyName] = useState('Ford')
  const [modelName, setModelName] = useState('Mustang GT')
  const [year, setYear] = useState(2025)
  const [color, setColor] = useState('Matte Black')
  const [seats, setSeats] = useState(4)
  const [cc, setCc] = useState(5000)

  // Output States
  const [matchedCompanyName, setMatchedCompanyName] = useState('')
  const [matchedCarName, setMatchedCarName] = useState('')
  const [matchedPrice, setMatchedPrice] = useState(null)
  const [predictedPrice, setPredictedPrice] = useState(null)
  const [prediction, setPrediction] = useState(null) // 0-100 performance

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (started) {
      // Fetch statistics
      fetch('http://127.0.0.1:8000/api/cars/stats')
        .then(res => res.json())
        .then(data => {
          setStats(data)
          setLoading(false)
        })
        .catch(err => console.error(err))
    }
  }, [started])

  const handlePredict = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/search_car', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: companyName,
          model_name: modelName,
          year: Number(year),
          color: color,
          seats: Number(seats),
          cc_capacity: Number(cc)
        })
      })
      const data = await res.json()
      setMatchedCompanyName(data.matched_company_name)
      setMatchedCarName(data.matched_car_name)
      setMatchedPrice(data.matched_price)
      setPredictedPrice(data.predicted_price)
      setPrediction(data.predicted_performance_0_100)
    } catch (err) {
      console.error(err)
    }
  }

  if (!started) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
        <h1 className="text-7xl font-extrabold mb-8 tracking-tighter">
          Car <span className="text-gradient">Evolution</span>
        </h1>
        <p className="text-2xl text-slate-400 mb-12 max-w-2xl">
          Experience the evolution of automotive engineering, powered by AI models analyzing thousands of vehicles.
        </p>
        <button 
          onClick={() => setStarted(true)}
          className="group relative px-12 py-6 font-bold text-2xl rounded-full bg-blue-600 text-white overflow-hidden transition-all hover:bg-blue-500 hover:scale-105 shadow-[0_0_40px_rgba(37,99,235,0.5)]"
        >
          <span className="relative z-10">START EVOLUTION</span>
          <div className="absolute inset-0 h-full w-full bg-gradient-to-r from-blue-600 via-emerald-500 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8 transition-opacity duration-1000 overflow-y-auto">
      <header className="max-w-6xl mx-auto mb-12 text-center mt-6">
        <h1 className="text-5xl font-extrabold mb-4 tracking-tight">
          Car <span className="text-gradient">Evolution</span> System
        </h1>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: System Stats */}
        <div className="flex flex-col gap-8">
          <div className="metric-card glass-panel">
            <h2 className="text-xl font-semibold text-slate-400 mb-2">Total Vehicles</h2>
            <p className="text-5xl font-bold text-emerald-400">
              {loading ? '...' : stats.total_cars.toLocaleString()}
            </p>
          </div>

          <div className="metric-card glass-panel">
            <h2 className="text-xl font-semibold text-slate-400 mb-2">System Status</h2>
            <div className="flex items-center space-x-2 mt-4">
              <span className="h-4 w-4 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_15px_rgba(16,185,129,0.8)]"></span>
              <span className="text-xl text-emerald-400 font-medium tracking-wide">AI Models Online</span>
            </div>
          </div>
        </div>

        {/* Center/Right Column: ML Evolution Predictor */}
        <div className="lg:col-span-2 metric-card glass-panel flex flex-col items-center p-8">
          <h2 className="text-2xl font-bold text-slate-300 mb-6 border-b border-slate-700 pb-2 w-full text-left">
            Evolution Criteria & AI Prediction
          </h2>
          
          <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 text-left">
            {/* Left Column: Vehicle Identity */}
            <div className="space-y-4">
              <h3 className="text-blue-400 font-semibold mb-2">Design & Identity</h3>
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Company/Brand</label>
                <input 
                  type="text" 
                  value={companyName} 
                  onChange={(e) => setCompanyName(e.target.value)} 
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-blue-500" 
                  placeholder="e.g. Ford, Ferrari"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Car Model</label>
                <input 
                  type="text" 
                  value={modelName} 
                  onChange={(e) => setModelName(e.target.value)} 
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-blue-500" 
                  placeholder="e.g. Mustang, SF90"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Model Year</label>
                  <input 
                    type="number" 
                    value={year} 
                    onChange={(e) => setYear(e.target.value)} 
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-blue-500" 
                    placeholder="2025"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Colour</label>
                  <input 
                    type="text" 
                    value={color} 
                    onChange={(e) => setColor(e.target.value)} 
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-blue-500" 
                    placeholder="Matte Black"
                  />
                </div>
              </div>
            </div>

            {/* Right Column: Specifications */}
            <div className="space-y-4">
              <h3 className="text-emerald-400 font-semibold mb-2">Specifications</h3>
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Sitting Capacity (Seats)</label>
                <input 
                  type="number" 
                  value={seats} 
                  onChange={(e) => setSeats(e.target.value)} 
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-emerald-500" 
                  placeholder="4"
                  min="1"
                  max="10"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Engine Capacity (CC)</label>
                <input 
                  type="number" 
                  value={cc} 
                  onChange={(e) => setCc(e.target.value)} 
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-emerald-500" 
                  placeholder="5000"
                  min="100"
                  max="20000"
                />
                <input 
                  type="range"
                  min="500"
                  max="8000"
                  step="100"
                  value={cc}
                  onChange={(e) => setCc(e.target.value)}
                  className="w-full mt-2 accent-emerald-500 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
                  <span>500 CC</span>
                  <span>8000 CC</span>
                </div>
              </div>
            </div>
          </div>

          <button 
            onClick={handlePredict}
            className="w-full md:w-1/2 py-4 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white rounded-full font-bold text-lg transition-colors shadow-[0_0_20px_rgba(16,185,129,0.3)]"
          >
            Synthesize & Predict Evolution
          </button>
          
          {matchedCarName && (
            <div className="mt-8 p-6 bg-slate-900/60 rounded-xl w-full border border-slate-700 shadow-inner text-left">
              <span className="text-slate-400 block text-center uppercase tracking-widest text-xs font-semibold mb-4">
                Evolution Matching & Prediction Results
              </span>
              
              <div className="mb-6 p-4 bg-slate-800/40 rounded-lg border border-slate-700/50 text-center">
                <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">Closest Database Match</span>
                <p className="text-3xl font-black text-blue-400 drop-shadow-[0_0_10px_rgba(96,165,250,0.3)]">
                  {matchedCompanyName.toUpperCase()} {matchedCarName.toUpperCase()}
                </p>
                <p className="text-xs text-slate-400 mt-2">
                  Configuration searched: {year} {color} {companyName} {modelName} ({seats} seats, {cc} CC)
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-slate-800/40 rounded-lg border border-slate-700/50">
                  <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">Database Match Price</span>
                  <p className="text-2xl font-black text-emerald-400">
                    ₹{matchedPrice ? matchedPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : 'N/A'}
                  </p>
                </div>
                <div className="text-center p-4 bg-slate-800/40 rounded-lg border border-slate-700/50">
                  <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">AI Predicted Price</span>
                  <p className="text-2xl font-black text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.3)]">
                    ₹{predictedPrice ? predictedPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : 'N/A'}
                  </p>
                </div>
                <div className="text-center p-4 bg-slate-800/40 rounded-lg border border-slate-700/50">
                  <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">AI Predicted Performance</span>
                  <p className="text-2xl font-black text-blue-400">
                    {prediction ? `${prediction} sec` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App


