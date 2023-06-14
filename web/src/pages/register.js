import React, { Component } from "react";

import "../css/register.css";

export default class register extends Component {
  backend_url = "http://localhost:8000/";
  constructor(props) {
    super(props);

    this.state = {
      screenName: "",
      email: "",
      password: "",
      pwdError: "",
      fname: "",
      mname: "",
      lname: "",
      phone: "",
      not_entered: true,
    };
  }

  handleChange = async (e) => {
    await this.setState({ [e.target.name]: e.target.value });
  };

  handlePasswordChange = async (e) => {
    let pwd = e.target.value;

    if (!/[A-Z]/.test(pwd))
      await this.setState({
        pwdError: "Password must contain at least one upper case character",
      });
    else if (!/[a-z]/.test(pwd))
      await this.setState({
        pwdError: "Password must contain at least one lower case character",
      });
    else if (!/\d/.test(pwd))
      await this.setState({
        pwdError: "Password must contain at least one number",
      });
    // eslint-disable-next-line
    else if (!/[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/.test(pwd))
      await this.setState({
        pwdError: "Password must contain at least one special character (e.g. $, -, #, etc.)",
      });
    else if (pwd.length < 8 || pwd.length > 16)
      await this.setState({ pwdError: "Password should be of 8 - 16 characters long!" });
    else await this.setState({ pwdError: "" });
    await this.setState({ password: pwd, not_entered: false });
  };

  isEmpty(val) {
    return !/([^\s]*)/.test(val) || val === null || val.trim() === "";
  }

  submitDetails = async () => {
    if (this.isEmpty(this.state.screenName)) {
      alert("Screen Name cannot be empty");
      return;
    }
    if (this.isEmpty(this.state.email)) {
      alert("Email cannot be empty");
      return;
    }

    let pwd = this.state.password;

    if (
      // eslint-disable-next-line
      !/[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/.test(pwd) ||
      !/[A-Z]/.test(pwd) ||
      !/[a-z]/.test(pwd) ||
      !/\d/.test(pwd)
    ) {
      alert("Password conditions not met");
      return;
    }

    // extra check - marking these 3 values as null if they are empty since they are optional in backend
    if (this.isEmpty(this.state.fname)) await this.setState({ fname: null });
    if (this.isEmpty(this.state.lname)) await this.setState({ lname: null });
    if (this.isEmpty(this.state.mname)) await this.setState({ mname: null });

    let data = {
      screenName: this.state.screenName,
      email: this.state.email,
      password: this.state.password,
      fname: this.state.fname,
      mname: this.state.mname,
      lname: this.state.lname,
      phone: this.state.phone === "" ? null : JSON.stringify(this.state.phone), // phone number is string in backend
    };

    // registering in the backend
    try {
      let resp = await fetch(this.backend_url + "auth/register", {
        method: "POST",
        // mode: "cors",
        mode: "no-cors",
        cache: "no-cache",
        headers: {
          "Content-Type": "application/json",
          // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        referrerPolicy: "no-referrer",
        body: JSON.stringify(data),
      });

      console.log(resp);
    } catch (error) {
      console.log(error);
      alert("Failed to submit data! Server Error");
    }
  };

  submitDetailsTEST = async () => {
    let data = {
      screenName: "HAPPY_GUY",
      email: "hap@hap.com",
      password: "Abcd123$#",
      fname: "happu",
      mname: "naasd",
      lname: "asdasd",
      phone: "1234567890", // phone number is string in backend
    };

    // registering in the backend

    let headers = new Headers();

    headers.append("Content-Type", "application/json");
    headers.append("Accept", "application/json");

    headers.append("Access-Control-Allow-Origin", "http://localhost:3000");
    headers.append("Access-Control-Allow-Credentials", "true");
    headers.append("Access-Control-Allow-Methods", "POST");
    headers.append("Access-Control-Allow-Headers", "Content-Type, Authorization");

    headers.append("GET", "POST", "OPTIONS");

    try {
      // let resp = await fetch(this.backend_url + "register", {
      let resp = await fetch(this.backend_url + "auth/register", {
        method: "POST",
        credentials: "include",
        mode: "cors",
        cache: "no-cache",
        headers,
        referrerPolicy: "no-referrer",
        // body: JSON.stringify({ screenName: "HAPPY_GUY", email: "hap@hap.com", password: "Abcd123$#" }),
        body: JSON.stringify(data),
      });

      let res = await resp.json();
      console.log(resp);
      console.log(res);
    } catch (error) {
      console.log(error);
      alert("Failed to submit data! Server Error");
    }
  };

  render() {
    return (
      <React.Fragment>
        <div className="container register_container">
          <div className="container-fluid glass_card register_card">
            <h3 className="reg_title">SignUp</h3>
            <div className="fst-italic">
              (Fields marked <span className="text-danger">*</span> are required fields)
            </div>
            <br />
            <label>
              Screen Name <span className="text-danger">*</span>
            </label>
            <br />
            <input
              type={"text"}
              name="screenName"
              value={this.state.screenName}
              onChange={this.handleChange}
            ></input>
            <br />
            <br />
            <label>
              Email <span className="text-danger">*</span>
            </label>
            <br />
            <input type={"email"} name="email" value={this.state.email} onChange={this.handleChange}></input>
            <br />
            <br />
            <label>
              Password <span className="text-danger">*</span>
            </label>
            <br />
            <input
              type={"password"}
              name="password"
              value={this.state.password}
              onChange={this.handlePasswordChange}
            ></input>
            {!this.state.not_entered ? (
              <div className="text-danger fst-italic">{this.state.pwdError}</div>
            ) : null}
            <br />
            {/* <hr /> */}
            <label>First Name</label>
            <br />
            <input type={"text"} name="fname" value={this.state.fname} onChange={this.handleChange}></input>
            <br />
            <br />
            <label>Middle Name</label>
            <br />
            <input type={"text"} name="mname" value={this.state.mname} onChange={this.handleChange}></input>
            <br />
            <br />
            <label>Last Name</label>
            <br />
            <input type={"text"} name="lname" value={this.state.lname} onChange={this.handleChange}></input>
            <br />
            <br />
            <label>Phone number</label>
            <br />
            <input type={"number"} name="phone" value={this.state.phone} onChange={this.handleChange}></input>
            <br />
            <br />
            <button className="btn regiterBtn" onClick={this.submitDetails}>
              Sign Up
            </button>

            <button className="btn regiterBtn" onClick={this.submitDetailsTEST}>
              TEST
            </button>
          </div>
        </div>
      </React.Fragment>
    );
  }
}
