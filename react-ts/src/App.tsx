import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainLayout from "./components/shared/main-layout";
import Home from "./components/Home";


const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout><Home /></MainLayout>} />
      </Routes>
    </BrowserRouter>
  )
}
export default App;
