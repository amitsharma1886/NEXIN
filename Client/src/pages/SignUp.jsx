import React, { useState } from "react";

const Signup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:5000/api/users/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    const data = await res.json();
     if (res.ok) {
    alert("✅ User registered successfully! Please sign in.");
    navigate("/signin");
  } else {
    alert(data.message);
  }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-midnight-700">
      <div className="bg-midnight-800 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-bold text-center text-electric-400 mb-6">
          Create Account
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 bg-midnight-600 text-white rounded-full border border-midnight-500 focus:ring-2 focus:ring-electric-400 outline-none"
          />
          <input
            type="email"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 bg-midnight-600 text-white rounded-full border border-midnight-500 focus:ring-2 focus:ring-electric-400 outline-none"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 bg-midnight-600 text-white rounded-full border border-midnight-500 focus:ring-2 focus:ring-electric-400 outline-none"
          />
          <button
            type="submit"
            className="w-full px-4 py-2 rounded-full bg-gradient-to-r from-electric-500 to-electric-400 hover:from-electric-400 hover:to-electric-300 text-white transition-all shadow-glow-purple"
          >
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
};

export default Signup;
