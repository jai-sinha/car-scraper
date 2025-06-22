import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Layout from './Layout';
import Search from '../content/Search';
import NoMatch from '../content/NoMatch';

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Search />} />
          <Route path="*" element={<NoMatch />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
