import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { LoginStatusProvider } from "../contexts/LoginStatusContext";
import Layout from './Layout';
import Garage from '../content/Garage';
import Homepage from '../content/Homepage';
import NoMatch from '../content/NoMatch';
import Register from '../auth/Register'

function App() {

  return (
    <BrowserRouter>
      <LoginStatusProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Homepage />} />
            <Route path="*" element={<NoMatch />} />
            <Route path="garage" element={<Garage />} />
            <Route path="register" element={<Register />} />
          </Route>
        </Routes>
      </LoginStatusProvider>
    </BrowserRouter>
  );
}

export default App;
