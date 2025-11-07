import React from "react";
import "./HeaderBar.css"

export default function HeaderBar() {
  return (
    <div className="">
      <header className="header">
        <div className="brand">
          <img alt="Sonemica logo" className="logo" />
          <h1 className="brand-name">{"SONEMICA"}</h1>
        </div>
      </header>
    </div>
  );
}
