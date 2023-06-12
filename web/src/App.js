import "./App.css";
import { Switch, Route, BrowserRouter } from "react-router-dom";

import Register from "./pages/register";

function App() {
  return (
    <BrowserRouter>
      <Switch>
        {/* <PrivateRoute exact path="/test/:id" component={Test}></PrivateRoute> */}
        <Route exact path="/register" component={Register}></Route>
        {/* <Route path="*" component={PageNotFound}></Route> */}
      </Switch>
    </BrowserRouter>
  );
}

export default App;
