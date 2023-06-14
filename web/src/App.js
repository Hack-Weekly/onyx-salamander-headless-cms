import "./App.css";
import { Switch, Route, BrowserRouter } from "react-router-dom";

import Register from "./pages/register";
import React from "react";

import Navbar from "./components/navbar";

function App() {
  return (
    <React.Fragment>
      <Navbar />
      <BrowserRouter>
        <Switch>
          {/* <PrivateRoute exact path="/test/:id" component={Test}></PrivateRoute> */}
          <Route exact path="/register" component={Register}></Route>
          {/* <Route path="*" component={PageNotFound}></Route> */}
        </Switch>
      </BrowserRouter>
    </React.Fragment>
  );
}

export default App;
