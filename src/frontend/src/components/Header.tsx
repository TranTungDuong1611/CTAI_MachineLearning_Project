import React from "react";
import { NavLink } from "react-router-dom";
import verticalDivider from "../assets/verticaldivider.png";

interface NavigationTabProps {
  label: string;
  to: string;
  isHashTag?: boolean;
}

const NavigationTab: React.FC<NavigationTabProps> = ({
  label,
  to,
  isHashTag = false,
}) => {
  return (
    <NavLink
      to={to}
      style={{
        color: 'white',
        textDecoration: 'none'
      }}
      className={({ isActive }) =>
        `px-6 py-3 font-semibold text-base transition-all duration-300 ease-in-out transform hover:scale-105 ${
          isHashTag
            ? "bg-gradient-to-r from-indigo-500/30 to-purple-500/30 hover:from-indigo-500/40 hover:to-purple-500/40 rounded-full backdrop-blur-sm border border-white/10 shadow-lg"
            : isActive
            ? "bg-gradient-to-r from-teal-400 to-cyan-500 shadow-xl rounded-xl text-white font-bold"
            : "hover:text-yellow-300 hover:bg-white/10 rounded-lg relative after:absolute after:bottom-0 after:left-0 after:w-0 after:h-0.5 after:bg-yellow-300 after:transition-all after:duration-300 hover:after:w-full"
        }`
      }
    >
      {isHashTag ? `#${label}` : label}
    </NavLink>
  );
};

const Header: React.FC = () => {
  const mainTabs = [
    { label: "TRANG CHỦ", path: "/home" },
    { label: "PHÂN LOẠI - TÓM TẮT", path: "/classify-summarize" },
    { label: "CHỦ ĐỀ", path: "/clustering" },
  ];

  const hashTags = [
    { label: "Năng lượng tích cực", path: "/hashtag/positive-energy" },
    { label: "Nghị quyết 57", path: "/hashtag/resolution-57" },
    { label: "Khám phá Việt Nam", path: "/hashtag/explore-vietnam" },
  ];

  return (
    <header className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 shadow-2xl border-b-2 border-gray-700/50 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-400 via-cyan-500 to-indigo-500"></div>
      
      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="flex items-center py-6 min-h-[60px]">
          {/* Main Navigation */}
          <nav className="flex items-center">
            {mainTabs.map((tab, index) => (
              <React.Fragment key={tab.label}>
                <div style={index === 0 ? { marginLeft: '2rem' } : {}}>
                  <NavigationTab
                    label={tab.label}
                    to={tab.path}
                    isHashTag={false}
                  />
                </div>
                {index < mainTabs.length - 1 && (
                  <div
                    className="flex items-center"
                    style={index === 0 ? { marginLeft: '2rem', marginRight: '2rem' } : { marginLeft: '2rem', marginRight: '2rem' }}
                  >
                    <img 
                      src={verticalDivider} 
                      alt="divider" 
                      className="h-8 opacity-70 drop-shadow-sm"
                    />
                  </div>
                )}
              </React.Fragment>
            ))}
          </nav>
          
          {/* Spacer */}
          <div className="flex-1"></div>
          
          {/* Hashtag Navigation */}
          <nav className="flex items-center space-x-2 ml-8">
            {hashTags.map((tag, index) => (
              <React.Fragment key={tag.label}>
                <div style={index !== 0 ? { marginRight: '0.5rem' , marginLeft: '0.5rem' } : {marginRight: '0.5rem'}}>
                  <NavigationTab
                    label={tag.label}
                    to={tag.path}
                    isHashTag={true}
                  />
                </div>
                {index < hashTags.length - 1 && (
                  <div className="mx-4 flex items-center">
                    <img 
                      src={verticalDivider} 
                      alt="divider" 
                      className="h-8 opacity-70 drop-shadow-sm"
                    />
                  </div>
                )}
              </React.Fragment>
            ))}
          </nav>
        </div>
      </div>
      
      {/* Bottom gradient line */}
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-gray-600 to-transparent"></div>
    </header>
  );
};

export default Header;
