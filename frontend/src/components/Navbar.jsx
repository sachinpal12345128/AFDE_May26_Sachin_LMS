import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/books', label: 'Books' },
  { to: '/borrowers', label: 'Borrowers' },
  { to: '/transactions', label: 'Transactions' },
  { to: '/search', label: 'Search' },
  { to: '/analytics', label: 'Analytics' },
];

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand">
          <span className="brand-icon">LMS</span>
          <span>Library Management System</span>
        </div>
        <nav className="nav-links">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) =>
                'nav-link' + (isActive ? ' active' : '')
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
