import { Route, Routes } from "react-router-dom";
import RequireOwner from "./components/RequireOwner";
import Chat from "./pages/Chat";
import Library from "./pages/Library";

export default function App() {
  return (
    <Routes>
      <Route element={<RequireOwner />}>
        <Route path="/" element={<Library />} />
        <Route path="/d/:id" element={<Chat />} />
      </Route>
    </Routes>
  );
}
