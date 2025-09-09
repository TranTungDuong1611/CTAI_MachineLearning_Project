import { NavLink } from "react-router-dom";

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
      className={({ isActive }) =>
        `px-4 py-2 font-medium text-sm transition-all duration-200 rounded-lg ${
          isHashTag
            ? "bg-white/20 text-white hover:bg-white/30"
            : isActive
            ? "text-white bg-teal-500 shadow-md"
            : "text-white hover:text-yellow-300 hover:underline"
        }`
      }
    >
      {isHashTag ? `#${label}` : label}
    </NavLink>
  );
};

const Header: React.FC = () => {
  // const mainTabs = ["TRANG CHỦ", "PHÂN LOẠI - TÓM TẮT", "CHỦ ĐỀ"];
  // const hashTags = ["Năng lượng tích cực", "Nghị quyết 57", "Khám phá Việt Nam"];

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
    <header className="bg-white shadow-sm">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center space-x-1 py-3 border-b">
          {mainTabs.map((tab) => (
            <NavigationTab
              key={tab.label}
              label={tab.label}
              to={tab.path}
              isHashTag={false}
            />
          ))}
          <div className="flex-1"></div>
          <div className="flex items-center space-x-2">
            {hashTags.map((tag) => (
              <NavigationTab
                key={tag.label}
                label={tag.label}
                to={tag.path}
                isHashTag={true}
              />
            ))}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
