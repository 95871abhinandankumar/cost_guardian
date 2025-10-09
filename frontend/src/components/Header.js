import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <h1>Cost Guardian</h1>
      <nav>
        <ul>
          <li><a href="/">Dashboard</a></li>
          <li><a href="/expenses">Expenses</a></li>
          <li><a href="/budget">Budget</a></li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
