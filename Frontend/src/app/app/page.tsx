"use client";

import { useState } from "react";
// Make sure to install heroicons: npm install @heroicons/react
import { ClipboardIcon, TrashIcon, CheckIcon } from "@heroicons/react/24/outline";


// --- Helper Components ---

const Spinner = () => (
    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
);

const ResultsTable = ({ data }) => {
    // Handle cases where data is not an array (e.g., { "rows_affected": 1 })
    if (!Array.isArray(data)) {
        // If it's an object, display it as a simple key-value table
        if (typeof data === 'object' && data !== null) {
             return (
                <div className="overflow-x-auto bg-gray-900/80 rounded-xl mt-4 border border-gray-700">
                    <table className="min-w-full text-sm text-left">
                        <tbody>
                            {Object.entries(data).map(([key, value]) => (
                                <tr key={key} className="hover:bg-gray-700/50">
                                    <th className="px-4 py-2 border-b border-gray-700 text-purple-300 font-semibold">{key}</th>
                                    <td className="px-4 py-2 border-b border-gray-700">{String(value)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        }
        // Fallback for non-array, non-object data
        return <p className="text-center text-gray-400 mt-4">{String(data)}</p>;
    }

    if (data.length === 0) {
        return <p className="text-center text-gray-400 mt-4">Query executed successfully, but returned no rows.</p>;
    }

    const headers = Object.keys(data[0]);

    return (
        <div className="overflow-x-auto bg-gray-900/80 rounded-xl mt-4 border border-gray-700">
            <table className="min-w-full text-sm text-left border-collapse">
                <thead>
                    <tr className="bg-gray-800/50">
                        {headers.map((key) => (
                            <th key={key} className="px-4 py-2 border-b border-gray-700 text-purple-300 font-semibold">
                                {key}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, idx) => (
                        <tr key={idx} className="hover:bg-gray-700/50">
                            {headers.map((header, i) => (
                                <td key={i} className="px-4 py-2 border-b border-gray-700">
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
    const [history, setHistory] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isExecuting, setIsExecuting] = useState(false);
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState(null);

    const API_BASE_URL = "http://127.0.0.1:8000";

    const handleGenerateSql = async () => {
        if (!query.trim()) return;

        setIsGenerating(true);
        setSql("");
        setResult(null);
        setError(null);

        try {
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
            setHistory((prev) => [query, ...prev.slice(0, 4)]);
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
        setError(null);

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

    const clearAll = () => {
        setQuery("");
        setSql("");
        setError(null);
        setResult(null);
    };

    const copyToClipboard = () => {
        if (!sql) return;
        const textArea = document.createElement("textarea");
        textArea.value = sql;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
        document.body.removeChild(textArea);
    };

    return (
        <main className="min-h-screen bg-gray-900 text-white flex flex-col font-sans">
            <header className="px-6 md:px-8 py-4 flex justify-between items-center bg-gray-900/50 backdrop-blur-lg border-b border-gray-700">
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                    NaturalSQL
                </h1>
                <a href="#" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                    Powered by FastAPI & Groq
                </a>
            </header>

            <section className="flex flex-1 flex-col md:flex-row gap-6 p-6 md:p-8">
                {/* Left Panel */}
                <div className="flex-1 flex flex-col bg-gray-800/60 backdrop-blur-md rounded-2xl p-6 shadow-2xl border border-gray-700">
                    <h2 className="text-xl font-semibold mb-4 text-gray-200">Ask in plain English</h2>
                    <textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="e.g. Show me all customers from London who have more than 5 orders"
                        className="w-full h-36 p-4 rounded-lg bg-gray-900 text-gray-200 border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                    />
                    <div className="flex gap-4 mt-4">
                        <button
                            onClick={handleGenerateSql}
                            disabled={isGenerating}
                            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center"
                        >
                            {isGenerating && <Spinner />} {isGenerating ? "Generating..." : "Generate SQL"}
                        </button>
                        <button onClick={clearAll} className="bg-gray-700 px-6 py-2.5 rounded-lg font-semibold hover:bg-gray-600 transition-colors">
                            Clear
                        </button>
                    </div>

                    <div className="flex-grow min-h-[2rem]"></div>

                    {/* SQL Output Section */}
                    {(sql || isGenerating) && (
                        <div className="mt-6">
                            <h3 className="font-semibold mb-2 text-gray-300">Generated SQL</h3>
                            <div className="bg-black text-green-300 font-mono p-4 rounded-lg relative border border-gray-700 min-h-[120px]">
                                {isGenerating ? (
                                    <div className="text-gray-400">Thinking...</div>
                                ) : (
                                    <>
                                        <pre className="whitespace-pre-wrap text-sm">{sql}</pre>
                                        <button onClick={copyToClipboard} className="absolute top-3 right-3 p-1.5 rounded-md bg-gray-700 hover:bg-gray-600 transition-colors">
                                            {copied ? <CheckIcon className="w-5 h-5 text-green-400" /> : <ClipboardIcon className="w-5 h-5 text-gray-300" />}
                                        </button>
                                    </>
                                )}
                            </div>
                            {sql && !isGenerating && (
                               <div className="text-center mt-4">
                                    <button
                                        onClick={handleExecuteSql}
                                        disabled={isExecuting}
                                        className="bg-gradient-to-r from-green-500 to-teal-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:from-green-600 hover:to-teal-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center mx-auto"
                                    >
                                        {isExecuting && <Spinner />} {isExecuting ? "Executing..." : "Execute SQL"}
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Right Panel */}
                <div className="w-full md:w-96 flex flex-col bg-gray-800/60 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700">
                    <div className="p-6 border-b border-gray-700">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold text-gray-200">Recent Queries</h2>
                            <button onClick={() => setHistory([])} title="Clear history">
                                <TrashIcon className="w-5 h-5 text-gray-400 cursor-pointer hover:text-red-400 transition-colors" />
                            </button>
                        </div>
                        <ul className="space-y-3 text-sm text-gray-300">
                            {history.length === 0 && <li className="text-gray-500 italic">Your recent queries will appear here.</li>}
                            {history.map((h, i) => (
                                <li key={i} className="bg-gray-900/50 rounded-lg px-3 py-2 hover:bg-gray-700/70 cursor-pointer transition-colors" onClick={() => setQuery(h)}>
                                    {h}
                                </li>
                            ))}
                        </ul>
                    </div>
                    {/* Execution Result Section */}
                    <div className="p-6 flex-1 overflow-y-auto">
                         <h2 className="text-lg font-semibold text-gray-200 text-center">Execution Result</h2>
                        {(result || error || isExecuting) && (
                            <div className="mt-4">
                                {isExecuting ? (
                                    <div className="flex justify-center items-center h-full"> <Spinner /> <span className="ml-2">Running query...</span></div>
                                ) : error ? (
                                    <div className="bg-red-900/50 text-red-200 p-3 rounded-lg border border-red-700">
                                        <p className="font-bold mb-1">An error occurred:</p>
                                        <pre className="whitespace-pre-wrap text-sm">{error}</pre>
                                    </div>
                                ) : (
                                    <ResultsTable data={result} />
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </section>
        </main>
    );
}

