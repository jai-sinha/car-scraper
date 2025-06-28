import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Layout from './Layout';
import Search from '../content/Search';
import Homepage from '../content/Homepage';
import NoMatch from '../content/NoMatch';
import Register from '../auth/Register'

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Homepage />} />
          <Route path="*" element={<NoMatch />} />
          <Route path="register" element={<Register />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
