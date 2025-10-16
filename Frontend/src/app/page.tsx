"use client";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 flex flex-col justify-center items-center text-white font-sans relative overflow-hidden p-8">
      {/* Background Glow */}
      <div className="absolute top-[-200px] left-[-200px] w-[400px] h-[400px] bg-white/20 blur-3xl rounded-full animate-pulse"></div>
      <div className="absolute bottom-[-200px] right-[-200px] w-[400px] h-[400px] bg-pink-400/20 blur-3xl rounded-full animate-pulse delay-1000"></div>

      {/* Content Container */}
      <section className="flex flex-col md:flex-row items-center justify-between max-w-6xl w-full py-20 gap-12 relative z-10">
        
        {/* Text Section */}
        <div className="flex-1 text-center md:text-left">
          <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-6">
            Transforming <span className="text-yellow-300">Natural Language</span> into SQL Queries
          </h1>
          <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-lg mx-auto md:mx-0">
            No SQL knowledge? No problem. Type your question in plain English, 
            and our AI instantly gives you the SQL query to access your data.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center md:justify-start gap-4">
             <button
              className="bg-yellow-300 text-blue-900 font-semibold px-8 py-3 rounded-lg shadow-lg hover:scale-105 hover:shadow-xl transition-transform duration-300 w-full sm:w-auto"
              onClick={() => window.location.href = '/demo'}
            >
              Live Demo
            </button>
            <button
              className="bg-white/20 text-white font-semibold px-8 py-3 rounded-lg shadow-lg hover:bg-white/30 transition-colors duration-300 w-full sm:w-auto"
              onClick={() => window.location.href = '/app'}
            >
              Open App
            </button>
          </div>
        </div>

        {/* Image / Illustration Section */}
        <div className="flex-1 flex justify-center mt-12 md:mt-0">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-xl hover:scale-105 transition-transform duration-500">
            <img
              src="/illustration.jpg"
              alt="Data visualization illustration"
              className="rounded-xl w-[400px] md:w-[500px] h-auto"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="absolute bottom-6 text-sm text-gray-200">
        © {new Date().getFullYear()} NaturalSQL
      </footer>
    </main>
  );
}

