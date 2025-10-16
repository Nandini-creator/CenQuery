"use client";

import { useState } from "react";

// --- Helper Components ---

// A simple loading spinner
const Spinner = () => (
    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
);

// A reusable table for displaying results
const ResultsTable = ({ data }) => {
    if (!data || data.length === 0) {
        return <p className="text-center text-gray-300 mt-4">No results to display.</p>;
    }

    const headers = Object.keys(data[0]);

    return (
        <div className="overflow-x-auto bg-white/10 rounded-xl mt-6">
            <table className="min-w-full text-sm text-left border-collapse">
                <thead>
                    <tr>
                        {headers.map((key) => (
                            <th key={key} className="px-4 py-2 border-b border-white/20 text-yellow-300 font-semibold">
                                {key}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, idx) => (
                        <tr key={idx} className="hover:bg-white/10">
                            {headers.map((header, i) => (
                                <td key={i} className="px-4 py-2 border-b border-white/10">
                                    {String(row[header])}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// --- Main Page Component ---

export default function DemoPage() {
    // State management
    const [query, setQuery] = useState("");
    const [sql, setSql] = useState("");
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [isExecuting, setIsExecuting] = useState(false);
    const [copyMessage, setCopyMessage] = useState("");

    const API_BASE_URL = "http://127.0.0.1:8000";

    const examples = [
        "What is the total population of Maharashtra in 2011?",
        "Show me the number of literate and illiterate people in Chennai",
        "Which district in Tamil Nadu has the most households?",
        "List all data for districts starting with 'coim'",
        "Add population data for Thane with 1.8m male and 1.6m female in 2011"
    ];

    const handleGenerateSql = async () => {
        if (!query.trim()) return;
        
        setIsGenerating(true);
        setSql("");
        setResult(null);
        setError("");

        try {
            // We intelligently choose the endpoint based on the question's keywords
            const isSelectQuery = ["what", "show", "list", "which", "how many", "count"].some(keyword => query.toLowerCase().startsWith(keyword));
            const generateEndpoint = isSelectQuery ? "/generate-select-sql" : "/generate-other-sql";

            const genResponse = await fetch(`${API_BASE_URL}${generateEndpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: query }),
            });

            if (!genResponse.ok) {
                const errData = await genResponse.json();
                throw new Error(errData.detail || "Failed to generate SQL.");
            }

            const genData = await genResponse.json();
            setSql(genData.sql_query);

        } catch (err) {
            setError(err.message);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleExecuteSql = async () => {
        if (!sql) return;

        setIsExecuting(true);
        setResult(null);
        setError("");

        try {
             const execResponse = await fetch(`${API_BASE_URL}/execute-sql`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sql_query: sql, question: query }),
            });

            if (!execResponse.ok) {
                const errData = await execResponse.json();
                throw new Error(errData.detail || "Failed to execute SQL.");
            }

            const execData = await execResponse.json();
            if (execData.status === "error") {
                setError(String(execData.result));
            } else {
                setResult(execData.result);
            }
        } catch(err) {
            setError(err.message);
        } finally {
            setIsExecuting(false);
        }
    };
    
    // --- UI Helpers ---

    const copySQL = () => {
        if (!sql) return;
        navigator.clipboard.writeText(sql);
        setCopyMessage("Copied!");
        setTimeout(() => setCopyMessage(""), 2000); // Hide message after 2 seconds
    };

    const downloadSQL = () => {
        if (!sql) return;
        const blob = new Blob([sql], { type: "text/sql" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "query.sql";
        link.click();
        URL.revokeObjectURL(link.href);
    };

    return (
        <main className="min-h-screen bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 text-white font-sans flex flex-col items-center p-8">
            <header className="text-center mb-10">
                <h1 className="text-4xl font-bold mb-3">Census Data SQL Generator</h1>
                <p className="text-gray-200">Type a question in plain English or click an example below.</p>
            </header>

            {/* Example Queries */}
            <div className="flex flex-wrap justify-center gap-3 mb-6 max-w-4xl">
                {examples.map((ex) => (
                    <button
                        key={ex}
                        onClick={() => setQuery(ex)}
                        className="bg-white/20 hover:bg-white/30 text-sm px-4 py-2 rounded-full transition"
                    >
                        {ex}
                    </button>
                ))}
            </div>

            {/* Input Box */}
            <textarea
                className="w-full max-w-3xl h-24 p-3 rounded-lg text-gray-900 outline-none mb-4 shadow-lg focus:ring-4 focus:ring-yellow-300 transition"
                placeholder="e.g., Show average household count by state"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
            />

            {/* Action Button */}
            <button
                onClick={handleGenerateSql}
                disabled={isGenerating}
                className={`px-8 py-3 font-semibold rounded-lg shadow-lg transition flex items-center justify-center ${
                    isGenerating
                        ? "bg-yellow-400/50 cursor-not-allowed"
                        : "bg-yellow-300 text-blue-900 hover:scale-105"
                }`}
            >
                {isGenerating ? <><Spinner /> Generating...</> : "Generate SQL"}
            </button>

            {/* --- Results Section --- */}
            <section className="mt-12 w-full max-w-5xl">
                {sql && (
                    <div className="mb-8">
                        <h2 className="text-2xl font-semibold mb-2 text-center">Generated SQL</h2>
                        <div className="bg-gray-900 text-green-200 p-4 rounded-lg w-full relative">
                            <pre className="overflow-auto text-sm whitespace-pre-wrap">{sql}</pre>
                            <div className="flex justify-end mt-2 gap-3 relative">
                                <span className="text-yellow-300 text-xs absolute left-4 bottom-1 transition-opacity duration-300">{copyMessage}</span>
                                <button onClick={copySQL} className="text-xs bg-white/10 hover:bg-white/20 px-3 py-1 rounded-lg">Copy</button>
                                <button onClick={downloadSQL} className="text-xs bg-white/10 hover:bg-white/20 px-3 py-1 rounded-lg">Download</button>
                            </div>
                        </div>
                        {/* Execute Button appears after SQL is generated */}
                         <div className="text-center mt-4">
                            <button
                                onClick={handleExecuteSql}
                                disabled={isExecuting}
                                className={`px-8 py-3 font-semibold rounded-lg shadow-lg transition flex items-center justify-center mx-auto ${
                                    isExecuting
                                        ? "bg-green-400/50 cursor-not-allowed"
                                        : "bg-green-400 text-blue-900 hover:scale-105"
                                }`}
                            >
                                {isExecuting ? <><Spinner /> Executing...</> : "Execute SQL"}
                            </button>
                        </div>
                    </div>
                )}

                {(result || error) && (
                     <div>
                        <h2 className="text-2xl font-semibold mb-2 text-center">Execution Result</h2>
                        {error ? (
                            <div className="bg-red-900/50 text-red-200 p-4 rounded-lg">
                                <p className="font-bold">An error occurred:</p>
                                <pre className="whitespace-pre-wrap text-sm">{error}</pre>
                            </div>
                        ) : (
                            <ResultsTable data={Array.isArray(result) ? result : [result]} />
                        )}
                    </div>
                )}
            </section>
        </main>
    );
}

