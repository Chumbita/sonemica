import { Routes, Route } from "react-router-dom";
import HomePage from "../pages/HomePage";
import Loading from "../pages/Loading";
import Result from "../pages/Result";
import CallbackPage from "../pages/CallbackPage";

export default function AppRouter() {
  return (
    <div>
      <Routes>
        <Route path="/home" element={<HomePage />} />
        <Route path="/loading" element={<Loading />} />
        <Route path="/results" element={<Result/>} />
        <Route path="/callback" element={<CallbackPage/>} />
      </Routes>
    </div>
  );
}
