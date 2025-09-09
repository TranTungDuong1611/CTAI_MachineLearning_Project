import VerticalDivider from '../assets/verticaldivider.png';
import { InstagramOutlined, FacebookOutlined, YoutubeOutlined } from '@ant-design/icons';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white py-8 mt-12">
          <div className="max-w-6xl mx-auto px-4">
                <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-400">
                </div>
            <div className="grid grid-cols-4 gap-8">
                <div>
                    <h3 className="text-lg font-semibold mb-4 ">Về chúng tôi</h3>
                    <p className="text-gray-300 text-sm">
                        Website tin tức hàng đầu Việt Nam, cập nhật thông tin nhanh chóng và chính xác.
                    </p>
                </div>
                <div>
                    <h3 className="text-lg font-semibold mb-4">Chuyên mục</h3>
                    <ul className="space-y-2 text-sm text-gray-300">
                        <li><a href="#" className="hover:text-white">Thời sự</a></li>
                        <li><a href="#" className="hover:text-white">Thể thao</a></li>
                        <li><a href="#" className="hover:text-white">Kinh tế</a></li>
                        <li><a href="#" className="hover:text-white">Giải trí</a></li>
                    </ul>
                </div>
                <div>
                    <h3 className="text-lg font-semibold mb-4">Liên hệ</h3>
                    <div className="text-sm text-gray-300 space-y-2">
                        <p><i className="fas fa-phone mr-2"></i>1900 123 456</p>
                        <p><i className="fas fa-envelope mr-2"></i>info@news.vn</p>
                        <p><i className="fas fa-map-marker-alt mr-2"></i>Hà Nội, Việt Nam</p>
                    </div>
                </div>
                <div>
                      <h3 className="text-lg font-semibold mb-4">Theo dõi chúng tôi</h3>
                        <div className="SocialIcon flex items-center gap-12">
                            <div className="Icon block">
                                <a href="#" aria-label="Facebook">
                                <FacebookOutlined style={{ fontSize: '36px', color: '#fefefe' }} />
                                </a>
                            </div>
                            <div className="Icon block">
                                <a href="#" aria-label="Instagram">
                                <InstagramOutlined style={{ fontSize: '36px', color: '#fefefe' }} />
                                </a>
                            </div>
                            <div className="Icon block">
                                <a href="#" aria-label="YouTube">
                                <YoutubeOutlined style={{ fontSize: '36px', color: '#fefefe' }} />
                                </a>
                            </div>
                        </div>
                  </div>
              </div>
              <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-400">
                  <p>&copy; 2024 Vietnamese News Website. Tất cả quyền được bảo lưu.</p>
              </div>
          </div>
      </footer>
  );
};

export default Footer;