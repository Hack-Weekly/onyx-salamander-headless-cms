import React, { Component } from "react";

export default class navbar extends Component {
  constructor(props) {
    super(props);
    // let isLoggedIn = localStorage.getItem("user") ? true : false;
    let isLoggedIn = false; // dev-test
    this.state = { isLoggedIn };
  }

  render() {
    return (
      <React.Fragment>
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
          <div className="container-fluid">
            <a className="navbar-brand" href="/">
              ONYX SALAMANDER CMS
            </a>
            <button
              className="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarNavDropdown"
              aria-controls="navbarNavDropdown"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNavDropdown">
              <ul className="navbar-nav">
                <li className="nav-item">
                  <a className="nav-link active" aria-current="page" href="/">
                    Home
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link" href="/blogs">
                    Blogs
                  </a>
                </li>
              </ul>
              <form className="d-flex">
                <a className="btn btn-outline-success" href="/login">
                  Login
                </a>{" "}
                &nbsp;&nbsp;
                <a className="btn btn-outline-success" href="/register">
                  Sign Up
                </a>
              </form>
            </div>
          </div>
        </nav>
      </React.Fragment>
    );
  }
}
