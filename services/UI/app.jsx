import React, { useState, useEffect } from 'react';
import './index.css';
import { Search, ShoppingCart, User, Menu, ChevronRight, ChevronLeft, Star, Heart, Home, Clock, Package, Check, X } from 'lucide-react';

const App = () => {
  const API_BASE = `${window.location.protocol}//${window.location.hostname}:8003`;  // dynamic user-service host

  // Login / history modal states
  const [showLogin, setShowLogin] = useState(false);
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [searchHistory, setSearchHistory] = useState([]);
  const [viewedHistory, setViewedHistory] = useState([]);

  // new frontend state
  const [token, setToken] = useState(() => localStorage.getItem('token') || '');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);


  // Quản lý trạng thái cho các trang khác nhau
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [cart, setCart] = useState([]);
  const [orderHistory, setOrderHistory] = useState([]);
  const [viewedProducts, setViewedProducts] = useState([]);
  const [notification, setNotification] = useState({ show: false, message: '', type: 'success' });
  const [pageTransition, setPageTransition] = useState(false);


  // Xử lý thêm vào giỏ hàng
  const addToCart = (product) => {
    // Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
    const existingProduct = cart.find(item => item.id === product.id);
    
    if (existingProduct) {
      // Nếu đã có, tăng số lượng
      setCart(cart.map(item => 
        item.id === product.id 
          ? {...item, quantity: item.quantity + 1} 
          : item
      ));
      setNotification({
        show: true,
        message: `Đã tăng số lượng ${product.name} trong giỏ hàng`,
        type: 'success'
      });
    } else {
      // Nếu chưa có, thêm mới với số lượng 1
      setCart([...cart, {...product, quantity: 1}]);
      setNotification({
        show: true,
        message: `Đã thêm ${product.name} vào giỏ hàng`,
        type: 'success'
      });
    }
    
    // Tự động ẩn thông báo sau 3 giây
    setTimeout(() => {
      setNotification({ show: false, message: '', type: 'success' });
    }, 3000);
  };

  // Xử lý mua hàng
  const checkout = () => {
    // Thêm vào lịch sử mua hàng
    const order = {
      id: Date.now(),
      date: new Date().toLocaleDateString(),
      products: [...cart],
      total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    };
    
    setOrderHistory([order, ...orderHistory]);
    // Xóa giỏ hàng sau khi mua hàng
    setCart([]);
    // Hiển thị thông báo
    setNotification({
      show: true,
      message: 'Đặt hàng thành công! Cảm ơn bạn đã mua hàng.',
      type: 'success'
    });
    
    // Tự động ẩn thông báo sau 3 giây
    setTimeout(() => {
      setNotification({ show: false, message: '', type: 'success' });
    }, 3000);
    
    // Chuyển đến trang lịch sử
    changePage('history');
  };

  // Xử lý chuyển đổi trang
  const changePage = (page, product = null) => {
    setPageTransition(true);
    
    // Đợi animation hoàn thành rồi mới chuyển trang
    setTimeout(() => {
      setCurrentPage(page);
      if (product) {
        setSelectedProduct(product);
      }
      setPageTransition(false);
    }, 300);
  };

  // Xử lý xem chi tiết sản phẩm
  const viewProductDetail = (product) => {
    setSelectedProduct(product);
    // Thêm vào sản phẩm đã xem
    if (!viewedProducts.find(item => item.id === product.id)) {
      setViewedProducts([product, ...viewedProducts.slice(0, 3)]);
    }
    changePage('product');
  };

  // Xử lý xóa sản phẩm khỏi giỏ hàng
  const removeFromCart = (productId) => {
    const productToRemove = cart.find(item => item.id === productId);
    if (productToRemove) {
      setNotification({
        show: true,
        message: `Đã xóa ${productToRemove.name} khỏi giỏ hàng`,
        type: 'info'
      });
      
      // Tự động ẩn thông báo sau 3 giây
      setTimeout(() => {
        setNotification({ show: false, message: '', type: 'success' });
      }, 3000);
    }
    
    setCart(cart.filter(item => item.id !== productId));
  };

  // Xử lý thay đổi số lượng sản phẩm trong giỏ hàng
  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => 
        item.id === productId 
          ? {...item, quantity: newQuantity} 
          : item
      ));
    }
  };

  // handle search and record history
  // Fetch and record search history
  const handleSearch = async () => {
    if (token) {
      await fetch(`${API_BASE}/me/history/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ text: searchQuery })
      });
    }
    setSearchResults(products.slice(0, 10));
    setCurrentPage('searchResults');
  };

  // === Load user history when token changes ===
  // Load user history when token changes
  useEffect(() => {
    if (!token) return;

    const fetchHistories = async () => {
      // Search history
      try {
        const resS = await fetch(`${API_BASE}/me/history/search`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resS.ok) {
          const data = await resS.json();
          setSearchHistory(Array.isArray(data) ? data : []);
        } else {
          setSearchHistory([]);
        }
      } catch {
        setSearchHistory([]);
      }

      // View history
      try {
        const resV = await fetch(`${API_BASE}/me/history/view`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resV.ok) {
          const data = await resV.json();
          setViewedHistory(Array.isArray(data) ? data : []);
        } else {
          setViewedHistory([]);
        }
      } catch {
        setViewedHistory([]);
      }
    };

    fetchHistories();
  }, [token]);

  const handleLogin = (username, password) => {
    fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password })
    })
    .then(res => res.json())
    .then(data => {
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setShowLogin(false);
      } else {
        console.error('Login failed');
      }
    });
  };

  // Khi click icon User: clear token và open login modal
  const handleUserIconClick = () => {
    localStorage.removeItem('token');
    setToken('');
    setShowLogin(true);
  };



 // Render login/history modal
  const renderModal = () => {
    if (!showLogin) return null;

    return (
      <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-lg">
          {!token ? (
            // ==== LOGIN FORM ====
            <>
              <h2 className="text-xl font-bold mb-4">Đăng nhập</h2>
              <input
                type="text"
                placeholder="Username"
                value={loginUsername}
                onChange={e => setLoginUsername(e.target.value)}
                className="w-full border rounded py-2 px-3 mb-3"
              />
              <input
                type="password"
                placeholder="Password"
                value={loginPassword}
                onChange={e => setLoginPassword(e.target.value)}
                className="w-full border rounded py-2 px-3 mb-4"
              />
              <div className="flex justify-end space-x-2">
                <button
                  className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                  onClick={() => setShowLogin(false)}
                >Hủy</button>
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={() => handleLogin(loginUsername, loginPassword)}
                >Đăng nhập</button>
              </div>
            </>
          ) : (
            // ==== USER HISTORY + LOGOUT ====
            <>
              <h2 className="text-xl font-bold mb-4">Lịch sử của bạn</h2>
              <div className="mb-4">
                <h3 className="font-semibold mb-2">🔍 Search History</h3>
                {searchHistory.length > 0 ? (
                  <ul className="list-disc list-inside max-h-40 overflow-auto">
                    {searchHistory.map((h, i) => (
                      <li key={i}>
                        {h.text} — {new Date(h.created_at).toLocaleString()}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">Chưa có lịch sử tìm kiếm.</p>
                )}
              </div>
              <div className="mb-4">
                <h3 className="font-semibold mb-2">👁️ Viewed History</h3>
                {viewedHistory.length > 0 ? (
                  <ul className="list-disc list-inside max-h-40 overflow-auto">
                    {viewedHistory.map((h, i) => (
                      <li key={i}>
                        {h.text} — {new Date(h.created_at).toLocaleString()}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">Chưa có lịch sử xem.</p>
                )}
              </div>
              <div className="flex justify-between">
                <button
                  className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                  onClick={() => setShowLogin(false)}
                >Đóng</button>
                <button
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                  onClick={() => {
                    localStorage.removeItem('token');
                    setToken('');
                    setSearchHistory([]);
                    setViewedHistory([]);
                    setShowLogin(false);
                  }}
                >Đăng xuất</button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  };
  // ============= DỮ LIỆU MẪU =============
  // Dữ liệu mẫu sản phẩm - có thể thay thế bằng API hoặc dữ liệu thực tế
  const products = [
    { 
      id: 1, 
      name: 'Laptop Gaming ASUS ROG Zephyrus G14', 
      price: 32990000, 
      originalPrice: 35990000, 
      image: '/api/placeholder/220/150', 
      specs: 'AMD Ryzen 9 7940HS, RAM 16GB, SSD 1TB, RTX 4070, 14" 2K 165Hz', 
      rating: 4.9, 
      reviews: 73, 
      discount: '-8%',
      category: 'laptop',
      brand: 'ASUS',
      description: 'ASUS ROG Zephyrus G14 là một trong những laptop gaming mỏng nhẹ mạnh mẽ nhất hiện nay. Được trang bị CPU AMD Ryzen 9 7940HS, GPU NVIDIA GeForce RTX 4070 8GB, màn hình 14" 2K 165Hz, hỗ trợ chơi game và đồ họa chuyên nghiệp.',
      stock: 12,
      comments: [
        { id: 1, user: 'nguyenvan', rating: 5, date: '15-05-2025', content: 'Máy chạy rất mượt, pin trâu, màn hình đẹp.' },
        { id: 2, user: 'trangtran', rating: 5, date: '02-05-2025', content: 'Đáng đồng tiền, thiết kế cực đẹp và chắc chắn.' },
      ]
    },
    { 
      id: 2, 
      name: 'PC GVN Intel i5-13400F/ VGA RTX 4060', 
      price: 22490000, 
      originalPrice: 23990000, 
      image: '/api/placeholder/220/150', 
      specs: 'i5-13400F, RTX 4060, RAM 16GB, SSD 500GB', 
      rating: 4.8, 
      reviews: 112, 
      discount: '-6%',
      category: 'pc',
      brand: 'GVN',
      description: 'PC GVN Gaming mang đến trải nghiệm gaming tuyệt vời với cấu hình mạnh mẽ: CPU Intel Core i5-13400F, Card đồ họa NVIDIA GeForce RTX 4060 8GB, RAM 16GB DDR4, SSD 500GB. Hỗ trợ chơi tốt các game AAA mới nhất ở mức setting cao.',
      stock: 20,
      comments: [
        { id: 1, user: 'leminh', rating: 5, date: '10-04-2025', content: 'Máy chạy mát, hiệu năng tốt, chơi game rất mượt.' },
        { id: 2, user: 'anhtu', rating: 4, date: '28-03-2025', content: 'Máy đẹp, ship nhanh, đóng gói cẩn thận.' },
      ]
    },
    { 
      id: 3, 
      name: 'Màn hình Dahua DHI-LM25-E231 25" IPS 180Hz', 
      price: 2190000, 
      originalPrice: 2390000, 
      image: '/api/placeholder/220/150', 
      specs: '25", IPS, 180Hz, 1ms, Full HD', 
      rating: 5.0, 
      reviews: 6, 
      discount: '-8%',
      category: 'monitor',
      brand: 'Dahua',
      description: 'Màn hình gaming Dahua DHI-LM25-E231 với tấm nền IPS, độ phân giải Full HD, tần số quét 180Hz và thời gian phản hồi 1ms, mang đến trải nghiệm chơi game mượt mà và không bị giật lag. Thiết kế viền mỏng, chân đế chắc chắn.',
      stock: 15,
      comments: [
        { id: 1, user: 'g*****89', rating: 5, date: '13-05-2025', content: 'Cực kì hài lòng vì nó thể làm được những thứ mà mình cần.' },
        { id: 2, user: 'ph****09', rating: 5, date: '10-05-2025', content: 'Cực kì hài lòng.' },
      ]
    },
    { 
      id: 4, 
      name: 'Chuột không dây Rapoo M21 Silent', 
      price: 150000, 
      originalPrice: 200000, 
      image: '/api/placeholder/220/150', 
      specs: 'Wireless 2.4GHz, DPI 1000, Pin AA', 
      rating: 4.6, 
      reviews: 89, 
      discount: '-25%',
      category: 'mouse',
      brand: 'Rapoo',
      description: 'Chuột không dây Rapoo M21 Silent với thiết kế nhỏ gọn, di chuyển êm ái không gây tiếng ồn, công nghệ không dây 2.4GHz ổn định, độ phân giải 1000 DPI, sử dụng pin AA có thể thay thế, thời lượng pin lên đến 12 tháng.',
      stock: 50,
      comments: [
        { id: 1, user: 'duc123', rating: 5, date: '20-04-2025', content: 'Chuột nhỏ gọn, không gây tiếng động, rất hợp cho công việc văn phòng.' },
        { id: 2, user: 'minh98', rating: 4, date: '15-04-2025', content: 'Sản phẩm tốt, giá hợp lý, dùng rất thích.' },
      ]
    },
    { 
      id: 5, 
      name: 'Bàn phím cơ Akko PC75B Plus', 
      price: 2390000, 
      originalPrice: 2690000, 
      image: '/api/placeholder/220/150', 
      specs: 'Kailh Box White Switch, RGB, 75%', 
      rating: 4.7, 
      reviews: 156, 
      discount: '-11%',
      category: 'keyboard',
      brand: 'Akko',
      description: 'Bàn phím cơ Akko PC75B Plus với layout 75% nhỏ gọn, switch Kailh Box White có độ nảy và phản hồi tốt, đèn nền RGB 16.8 triệu màu, kết nối có dây hoặc Bluetooth 5.0, hỗ trợ hot-swap thay switch dễ dàng.',
      stock: 18,
      comments: [
        { id: 1, user: 'gamerk', rating: 5, date: '05-05-2025', content: 'Phím gõ sướng tay, LED đẹp, kết nối ổn định.' },
        { id: 2, user: 'thuylinh', rating: 4, date: '20-04-2025', content: 'Thiết kế đẹp, gõ nghe sound thích tai, đáng mua.' },
      ]
    },
    { 
      id: 6, 
      name: 'Tai nghe HyperX Cloud Alpha', 
      price: 1890000, 
      originalPrice: 2290000, 
      image: '/api/placeholder/220/150', 
      specs: '7.1 Surround, Microphone tháo rời', 
      rating: 4.8, 
      reviews: 182, 
      discount: '-17%',
      category: 'headphone',
      brand: 'HyperX',
      description: 'Tai nghe gaming HyperX Cloud Alpha với âm thanh vòm 7.1, driver dual chamber mang đến âm bass mạnh mẽ và âm mid trong trẻo, mic có thể tháo rời, khung nhôm bền bỉ, đệm tai mềm mại thoải mái khi đeo lâu.',
      stock: 25,
      comments: [
        { id: 1, user: 'tuanpc', rating: 5, date: '01-05-2025', content: 'Âm thanh cực kỳ tốt, đeo thoải mái, mic thu âm rõ.' },
        { id: 2, user: 'hoangnam', rating: 5, date: '25-04-2025', content: 'Chất lượng build cao, âm thanh đỉnh, rất đáng tiền.' },
      ]
    },
  ];

  // Sản phẩm bán chạy nhất
  const bestSellers = products.slice(0, 4);
  
  // Sản phẩm gợi ý dựa trên recommendation system (giả lập)
  const recommendedProducts = products.slice(2, 6);

  // ============= COMPONENTS =============

  // Notification component
  const Notification = ({ show, message, type }) => {
    if (!show) return null;

    return (
      <div className="fixed top-20 right-4 z-50 animate-bounce">
        <div className={`flex items-center p-4 rounded-lg shadow-lg ${
          type === 'success' ? 'bg-green-500' : 
          type === 'error' ? 'bg-red-500' : 
          'bg-blue-500'
        } text-white max-w-md transition-all duration-300 transform`}>
          <div className="mr-3">
            {type === 'success' ? (
              <Check className="h-5 w-5" />
            ) : type === 'error' ? (
              <X className="h-5 w-5" />
            ) : (
              <span className="h-5 w-5 block rounded-full border-2 border-white"></span>
            )}
          </div>
          <div className="flex-1">{message}</div>
          <button 
            className="ml-4 text-white hover:text-gray-200"
            onClick={() => setNotification({ show: false, message: '', type: 'success' })}
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>
    );
  };

  // Header component
  const Header = () => (
    <header className="bg-red-600 text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-3">
          {/* Logo */}
          <div className="flex items-center">
            <div 
              className="text-xl font-bold mr-6 cursor-pointer hover:text-yellow-300 transition-colors"
              onClick={() => changePage('dashboard')}
            >
              TechShop
            </div>
            <button className="lg:hidden">
              <Menu size={24} />
            </button>
          </div>
          
          {/* Search */}
          <div className="hidden lg:flex items-center flex-1 max-w-xl mx-4">
            <div className="relative w-full">
              <input 
                type="text" 
                placeholder="Bạn cần tìm gì?" 
                className="w-full border border-gray-300 rounded-md py-2 px-4 pl-10 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
              />
              <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
            </div>
            <button className="ml-2 bg-yellow-500 text-white py-2 px-4 rounded-md hover:bg-yellow-600 transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95">
              Tìm
            </button>
          </div>
          
          {/* User menu */}
          <div className="flex items-center space-x-6">
            <div 
              className="cursor-pointer flex items-center transition-colors hover:text-yellow-300"
              onClick={() => changePage('cart')}
            >
              <ShoppingCart size={24} className="relative" />
              {cart.length > 0 && (
                <span className="absolute top-1 right-16 bg-yellow-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
                  {cart.reduce((sum, item) => sum + item.quantity, 0)}
                </span>
              )}
              <span className="ml-1 hidden md:inline">Giỏ hàng</span>
            </div>
            <div 
              className="cursor-pointer flex items-center transition-colors hover:text-yellow-300"
              onClick={() => changePage('history')}
            >
              <Clock size={24} />
              <span className="ml-1 hidden md:inline">Lịch sử</span>
            </div>
            <div className="cursor-pointer">
              <User size={24} />
            </div>
          </div>
        </div>
        
        {/* Mobile search */}
        <div className="lg:hidden flex items-center pb-3">
          <div className="relative w-full">
            <input 
              type="text" 
              placeholder="Bạn cần tìm gì?" 
              className="w-full border border-gray-300 rounded-md py-2 px-4 pl-10 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          </div>
          <button className="ml-2 bg-yellow-500 text-white py-2 px-4 rounded-md hover:bg-yellow-600 transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95">
            Tìm
          </button>
        </div>
      </div>
    </header>
  );

  // Navigation breadcrumb
  const Breadcrumb = ({ product }) => (
    <div className="bg-gray-100 py-2">
      <div className="container mx-auto px-4">
        <div className="flex items-center text-sm text-gray-600">
            <span 
            className="cursor-pointer hover:text-red-600 flex items-center transition-colors duration-200"
            onClick={() => changePage('dashboard')}
          >
            <Home size={14} className="mr-1" /> Trang chủ
          </span>
          {currentPage === 'product' && (
            <>
              <ChevronRight size={14} className="mx-2" />
              <span 
                className="cursor-pointer hover:text-red-600"
                onClick={() => setCurrentPage('dashboard')}
              >
                {product?.category === 'laptop' ? 'Laptop' : 
                 product?.category === 'pc' ? 'PC Gaming' : 
                 product?.category === 'monitor' ? 'Màn hình' : 
                 product?.category === 'mouse' ? 'Chuột' : 
                 product?.category === 'keyboard' ? 'Bàn phím' : 
                 product?.category === 'headphone' ? 'Tai nghe' : 'Sản phẩm'}
              </span>
              <ChevronRight size={14} className="mx-2" />
              <span className="truncate max-w-xs">{product?.name}</span>
            </>
          )}
          {currentPage === 'cart' && (
            <>
              <ChevronRight size={14} className="mx-2" />
              <span>Giỏ hàng</span>
            </>
          )}
          {currentPage === 'history' && (
            <>
              <ChevronRight size={14} className="mx-2" />
              <span>Lịch sử mua hàng</span>
            </>
          )}
        </div>
      </div>
    </div>
  );

  // Product card component
  const ProductCard = ({ product }) => (
    <div 
      className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 cursor-pointer"
      onClick={() => viewProductDetail(product)}
    >
      <div className="relative">
        <img src={product.image} alt={product.name} className="w-full h-40 object-cover transition-transform duration-300 hover:scale-105" />
        {product.discount && (
          <div className="absolute top-2 left-2 bg-red-600 text-white text-xs font-bold px-2 py-1 rounded">
            {product.discount}
          </div>
        )}
        <button 
          className="absolute top-2 right-2 bg-white p-1 rounded-full shadow-md hover:bg-gray-100 transform transition-transform hover:scale-110"
          onClick={(e) => {
            e.stopPropagation();
            // Thêm vào yêu thích (có thể bổ sung tính năng sau)
          }}
        >
          <Heart size={16} className="text-gray-500 hover:text-red-500" />
        </button>
      </div>
      <div className="p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-1 hover:text-blue-600 line-clamp-2 h-10">
          {product.name}
        </h3>
        <p className="text-xs text-gray-500 mb-2">{product.specs}</p>
        <div className="flex items-center mb-2">
          <Star size={14} className="text-yellow-400" />
          <span className="text-xs text-gray-600 ml-1">{product.rating} ({product.reviews})</span>
        </div>
        <div className="flex flex-col">
          <div className="text-xs text-gray-500 line-through">
            {product.originalPrice.toLocaleString()}₫
          </div>
          <div className="text-lg font-bold text-red-600">
            {product.price.toLocaleString()}₫
          </div>
        </div>
        <button 
          className="mt-3 w-full bg-red-600 hover:bg-red-700 text-white py-1.5 px-3 rounded-md text-sm font-medium transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95"
          onClick={(e) => {
            e.stopPropagation();
            addToCart(product);
          }}
        >
          Thêm vào giỏ
        </button>
      </div>
    </div>
  );

  // ============= PAGE COMPONENTS =============

  // Dashboard component
  const Dashboard = () => (
    <div className="min-h-screen bg-gray-100">
      {/* Banner */}
      <div className="container mx-auto px-4 py-4">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg overflow-hidden">
          <div className="flex flex-col md:flex-row items-center">
            <div className="p-6 md:p-10 text-white md:w-1/2">
              <h1 className="text-2xl md:text-4xl font-bold mb-4">
                Hệ thống gợi ý sản phẩm thông minh
              </h1>
              <p className="mb-6">
                Tìm kiếm sản phẩm phù hợp nhất với nhu cầu của bạn dựa trên công nghệ AI tiên tiến.
              </p>
              <button className="bg-white text-blue-600 font-medium py-2 px-6 rounded-md hover:bg-gray-100 transition-colors">
                Khám phá ngay
              </button>
            </div>
            <div className="md:w-1/2">
              <img 
                src="/api/placeholder/600/300" 
                alt="Banner" 
                className="w-full object-cover"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Sản phẩm đã xem */}
      {viewedProducts.length > 0 && (
        <div className="container mx-auto px-4 py-6">
          <div className="bg-white rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Sản phẩm đã xem</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {viewedProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sản phẩm được gợi ý cho bạn */}
      <div className="container mx-auto px-4 py-6">
        <div className="bg-white rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Gợi ý cho bạn</h2>
            <div className="flex items-center space-x-2">
              <button className="text-sm border border-gray-300 rounded-md px-3 py-1 hover:bg-gray-100">
                Phổ biến
              </button>
              <button className="text-sm border border-gray-300 rounded-md px-3 py-1 hover:bg-gray-100">
                Mới nhất
              </button>
              <button className="text-sm border border-gray-300 rounded-md px-3 py-1 bg-blue-600 text-white hover:bg-blue-700">
                Phù hợp nhất
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {recommendedProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </div>

      {/* Sản phẩm bán chạy */}
      <div className="container mx-auto px-4 py-6">
        <div className="bg-white rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">PC bán chạy</h2>
            <a href="#" className="text-blue-600 text-sm flex items-center hover:underline">
              Xem tất cả <ChevronRight size={16} />
            </a>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {bestSellers.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Product detail component
  const ProductDetail = ({ product }) => (
    <div className="min-h-screen bg-gray-100 pb-8">
      <div className="container mx-auto px-4 py-4">
        <div className="bg-white rounded-lg p-4">
          {/* Product Info */}
          <div className="flex flex-col md:flex-row">
            {/* Product Images */}
            <div className="md:w-2/5 p-4">
              <div className="mb-4">
                <img src={product.image} alt={product.name} className="w-full object-cover rounded-lg" />
              </div>
              <div className="flex space-x-2 overflow-auto">
                <img src={product.image} alt={product.name} className="w-20 h-20 object-cover rounded border-2 border-red-500" />
                <img src="/api/placeholder/80/80" alt="alt view" className="w-20 h-20 object-cover rounded border hover:border-red-500" />
                <img src="/api/placeholder/80/80" alt="alt view" className="w-20 h-20 object-cover rounded border hover:border-red-500" />
              </div>
            </div>
            
            {/* Product Details */}
            <div className="md:w-3/5 p-4">
              <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
              
              <div className="flex items-center mb-4">
                <div className="flex items-center">
                  <Star size={18} className="text-yellow-400" />
                  <span className="ml-1 text-gray-700">{product.rating}</span>
                </div>
                <span className="mx-2 text-gray-400">|</span>
                <span className="text-gray-700">{product.reviews} đánh giá</span>
                <span className="mx-2 text-gray-400">|</span>
                <span className="text-green-600">Còn hàng ({product.stock})</span>
              </div>
              
              <div className="mb-4">
                <div className="text-3xl font-bold text-red-600">{product.price.toLocaleString()}₫</div>
                <div className="text-gray-500 line-through">{product.originalPrice.toLocaleString()}₫</div>
                <div className="text-green-600 font-medium">Tiết kiệm: {(product.originalPrice - product.price).toLocaleString()}₫ ({product.discount})</div>
              </div>
              
              <div className="mb-6">
                <h2 className="font-semibold mb-2">Thông số kỹ thuật:</h2>
                <p className="text-gray-700">{product.specs}</p>
              </div>
              
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                <button 
                  className="bg-red-600 hover:bg-red-700 text-white py-3 px-6 rounded-md font-bold flex-1 flex items-center justify-center transition-all duration-300 hover:shadow-lg transform hover:scale-[1.02] active:scale-95"
                  onClick={() => addToCart(product)}
                >
                  MUA NGAY
                </button>
                <button 
                  className="border border-red-600 text-red-600 hover:bg-red-50 py-3 px-6 rounded-md font-bold flex-1 flex items-center justify-center transition-all duration-300 hover:shadow transform hover:scale-[1.02] active:scale-95"
                  onClick={() => addToCart(product)}
                >
                  THÊM VÀO GIỎ
                </button>
              </div>
            </div>
          </div>

          {/* Product Description */}
          <div className="mt-8 p-4">
            <h2 className="text-xl font-bold mb-4">Mô tả sản phẩm</h2>
            <div className="text-gray-700">
              <p>{product.description}</p>
            </div>
          </div>

          {/* Product Comments/Reviews */}
          <div className="mt-8 p-4">
            <h2 className="text-xl font-bold mb-4">Đánh giá & Nhận xét ({product.comments.length})</h2>
            <div className="space-y-4">
              {product.comments.map(comment => (
                <div key={comment.id} className="border-b pb-4">
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-bold">
                      {comment.user.charAt(0).toUpperCase()}
                    </div>
                    <div className="ml-3">
                      <div className="font-medium">{comment.user}</div>
                      <div className="text-gray-500 text-sm">{comment.date}</div>
                    </div>
                  </div>
                  <div className="flex mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star 
                        key={i} 
                        size={16} 
                        className={i < comment.rating ? "text-yellow-400" : "text-gray-300"} 
                        fill={i < comment.rating ? "#FBBF24" : "#D1D5DB"}
                      />
                    ))}
                  </div>
                  <p className="text-gray-700">{comment.content}</p>
                </div>
              ))}
            </div>
            
            {/* Add Review Form (Simplified) */}
            <div className="mt-6 bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold mb-2">Viết đánh giá của bạn</h3>
              <div className="flex mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    size={24} 
                    className="text-gray-300 cursor-pointer hover:text-yellow-400" 
                  />
                ))}
              </div>
              <textarea 
                className="w-full border rounded-md p-3 mb-3" 
                placeholder="Chia sẻ trải nghiệm của bạn với sản phẩm này..."
                rows="3"
              ></textarea>
              <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95">
                Gửi đánh giá
              </button>
            </div>
          </div>

          {/* Recommended Products (Similar) */}
          <div className="mt-8 p-4">
            <h2 className="text-xl font-bold mb-4">Sản phẩm tương tự</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {recommendedProducts.slice(0, 4).map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Cart component
  const Cart = () => (
    <div className="min-h-screen bg-gray-100 pb-8">
      <div className="container mx-auto px-4 py-4">
        <div className="bg-white rounded-lg p-4">
          <h1 className="text-2xl font-bold mb-4">Giỏ hàng của bạn</h1>
          
          {cart.length === 0 ? (
            <div className="text-center py-12">
              <div className="flex justify-center mb-4">
                <ShoppingCart size={64} className="text-gray-300" />
              </div>
              <h2 className="text-xl font-medium text-gray-500 mb-4">Giỏ hàng của bạn đang trống</h2>
              <button 
                className="bg-red-600 hover:bg-red-700 text-white py-2 px-6 rounded-md transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95"
                onClick={() => changePage('dashboard')}
              >
                Tiếp tục mua sắm
              </button>
            </div>
          ) : (
            <>
              {/* Cart Progress */}
              <div className="flex justify-between items-center py-4 mb-6 border-b">
                <div className="flex items-center space-x-2 text-red-600 font-semibold">
                  <div className="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center">1</div>
                  <span>Giỏ hàng</span>
                </div>
                <div className="w-24 h-1 bg-gray-200"></div>
                <div className="flex items-center space-x-2 text-gray-400">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">2</div>
                  <span>Thông tin đặt hàng</span>
                </div>
                <div className="w-24 h-1 bg-gray-200"></div>
                <div className="flex items-center space-x-2 text-gray-400">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">3</div>
                  <span>Thanh toán</span>
                </div>
                <div className="w-24 h-1 bg-gray-200"></div>
                <div className="flex items-center space-x-2 text-gray-400">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">4</div>
                  <span>Hoàn tất</span>
                </div>
              </div>
            
              {/* Cart Items */}
              <div className="mb-4">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="py-2 text-left">Sản phẩm</th>
                      <th className="py-2 text-center">Đơn giá</th>
                      <th className="py-2 text-center">Số lượng</th>
                      <th className="py-2 text-right">Thành tiền</th>
                      <th className="py-2 text-center">Xóa</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart.map(item => (
                      <tr key={item.id} className="border-b">
                        <td className="py-4">
                          <div className="flex items-center">
                            <img src={item.image} alt={item.name} className="w-20 h-20 object-cover rounded" />
                            <div className="ml-4">
                              <div className="font-medium">{item.name}</div>
                              <div className="text-sm text-gray-500">{item.specs}</div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 text-center">
                          <div className="text-red-600 font-medium">{item.price.toLocaleString()}₫</div>
                          <div className="text-gray-500 text-sm line-through">{item.originalPrice.toLocaleString()}₫</div>
                        </td>
                        <td className="py-4">
                                  <div className="w-8 h-8 flex items-center justify-center">
                            <button 
                              className="w-8 h-8 border border-gray-300 rounded-l flex items-center justify-center hover:bg-gray-100 transition-all duration-200 hover:shadow-sm transform hover:scale-[1.05] active:scale-95"
                              onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            >
                              -
                            </button>
                            <div className="w-12 h-8 border-t border-b border-gray-300 flex items-center justify-center">
                              {item.quantity}
                            </div>
                            <button 
                              className="w-8 h-8 border border-gray-300 rounded-r flex items-center justify-center hover:bg-gray-100 transition-all duration-200 hover:shadow-sm transform hover:scale-[1.05] active:scale-95"
                              onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            >
                              +
                            </button>
                          </div>
                        </td>
                        <td className="py-4 text-right font-bold">
                          {(item.price * item.quantity).toLocaleString()}₫
                        </td>
                        <td className="py-4 text-center">
                          <button 
                            className="text-red-600 hover:text-red-800"
                            onClick={() => removeFromCart(item.id)}
                          >
                            ×
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Cart Summary */}
              <div className="flex flex-col md:flex-row justify-between gap-6 mt-8">
                <div className="md:w-1/2">
                  <div className="mb-4">
                    <label className="block mb-2 font-medium">Mã khuyến mãi</label>
                    <div className="flex">
                      <input type="text" className="border rounded-l p-2 flex-1" placeholder="Nhập mã khuyến mãi" />
                      <button className="bg-blue-600 text-white rounded-r p-2 px-4 hover:bg-blue-700">Áp dụng</button>
                    </div>
                  </div>
                  <div>
                    <label className="block mb-2 font-medium">Ghi chú đơn hàng</label>
                    <textarea 
                      className="w-full border rounded p-2" 
                      placeholder="Ghi chú về đơn hàng, ví dụ: thời gian hay địa điểm giao hàng"
                      rows="3"
                    ></textarea>
                  </div>
                </div>
                <div className="md:w-1/2 bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-bold mb-4">Tổng tiền giỏ hàng</h3>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between">
                      <span>Tổng sản phẩm:</span>
                      <span>{cart.reduce((sum, item) => sum + item.quantity, 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Tạm tính:</span>
                      <span>{cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toLocaleString()}₫</span>
                    </div>
                    <div className="flex justify-between text-green-600">
                      <span>Giảm giá:</span>
                      <span>0₫</span>
                    </div>
                    <div className="flex justify-between border-t pt-2 font-bold text-xl">
                      <span>Tổng cộng:</span>
                      <span className="text-red-600">{cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toLocaleString()}₫</span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      className="flex-1 bg-gray-200 hover:bg-gray-300 py-3 px-4 rounded-md font-medium transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95"
                      onClick={() => changePage('dashboard')}
                    >
                      Tiếp tục mua hàng
                    </button>
                    <button 
                      className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 px-4 rounded-md font-medium transition-all duration-300 hover:shadow-lg transform hover:scale-[1.02] active:scale-95"
                      onClick={checkout}
                    >
                      Thanh toán
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );

  // Order history component
  const OrderHistory = () => (
    <div className="min-h-screen bg-gray-100 pb-8">
      <div className="container mx-auto px-4 py-4">
        <div className="bg-white rounded-lg p-4">
          <h1 className="text-2xl font-bold mb-4">Lịch sử mua hàng</h1>
          
          {orderHistory.length === 0 ? (
            <div className="text-center py-12">
              <div className="flex justify-center mb-4">
                <Package size={64} className="text-gray-300" />
              </div>
              <h2 className="text-xl font-medium text-gray-500 mb-4">Bạn chưa có đơn hàng nào</h2>
              <button 
                className="bg-red-600 hover:bg-red-700 text-white py-2 px-6 rounded-md transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95"
                onClick={() => changePage('dashboard')}
              >
                Bắt đầu mua sắm
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {orderHistory.map(order => (
                <div key={order.id} className="border rounded-lg p-4">
                  <div className="flex flex-col md:flex-row justify-between mb-4 pb-4 border-b">
                    <div>
                      <div className="font-medium">Đơn hàng #{order.id}</div>
                      <div className="text-sm text-gray-500">Đặt ngày: {order.date}</div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        Đã hoàn thành
                      </div>
                      <button className="text-blue-600 hover:underline text-sm">Xem chi tiết</button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {order.products.map(item => (
                      <div key={item.id} className="flex flex-col sm:flex-row items-start sm:items-center py-2">
                        <img src={item.image} alt={item.name} className="w-16 h-16 object-cover rounded" />
                        <div className="sm:ml-4 flex-1">
                          <div className="font-medium">{item.name}</div>
                          <div className="text-sm text-gray-500">{item.specs}</div>
                        </div>
                        <div className="text-sm text-gray-500">
                          {item.quantity} × {item.price.toLocaleString()}₫
                        </div>
                        <div className="font-medium text-red-600 sm:ml-4">
                          {(item.price * item.quantity).toLocaleString()}₫
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex justify-between mt-4 pt-4 border-t">
                    <div className="font-bold">Tổng tiền:</div>
                    <div className="font-bold text-red-600">{order.total.toLocaleString()}₫</div>
                  </div>
                  
                  <div className="flex justify-end mt-4">
                    <button className="mr-2 border border-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-50 transition-all duration-300 hover:shadow transform hover:scale-[1.02] active:scale-95">
                      Mua lại
                    </button>
                    <button className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-all duration-300 hover:shadow-md transform hover:scale-[1.02] active:scale-95">
                      Đánh giá
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // SearchResults component
  const SearchResults = () => (
    <div className="container mx-auto px-4 py-6">
      <h2 className="text-xl font-bold mb-4">Kết quả tìm kiếm cho “{searchQuery}”</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {searchResults.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </div>
  );

  // ============= MAIN APP RENDER =============
  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <header className="bg-red-600 text-white shadow-md">
        <div className="container mx-auto px-4 flex items-center justify-between py-3">
          <div className="flex items-center">
            <div className="text-xl font-bold cursor-pointer" onClick={() => setCurrentPage('dashboard')}>TechShop</div>
            <button className="ml-4 lg:hidden"><Menu size={24} /></button>
          </div>
          <div className="hidden lg:flex items-center flex-1 mx-4 max-w-xl">
            <div className="relative w-full">
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Bạn cần tìm gì?"
                className="w-full border border-gray-300 rounded-md py-2 px-4 pl-10 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
              />
              <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
            </div>
            <button onClick={handleSearch} className="ml-2 bg-yellow-500 text-white py-2 px-4 rounded-md hover:bg-yellow-600">Tìm</button>
          </div>
          <div className="flex items-center space-x-6">
            <div onClick={() => setCurrentPage('cart')}><ShoppingCart size={24}/></div>
            <div
                onClick={() =>
                  token
                    ? setCurrentPage('history')
                    : setShowLogin(true)
                }
                className="cursor-pointer"
              >
                <Clock size={24}/>
              </div>

            <div className="cursor-pointer" onClick={() => setShowLogin(true)}>
              <User size={24}/>
            </div>
          </div>
        </div>
      </header>

      <Breadcrumb product={selectedProduct} />
      <Notification show={notification.show} message={notification.message} type={notification.type} />

      {renderModal()}


      <main className={`flex-1 transition-opacity duration-300 ${pageTransition ? 'opacity-0' : 'opacity-100'}`}>
        {currentPage === 'searchResults' && <SearchResults />}
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'product' && selectedProduct && <ProductDetail product={selectedProduct} />}
        {currentPage === 'cart' && <Cart />}
        {currentPage === 'history' && <OrderHistory />}
      </main>

      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between">
          <div className="mb-6 md:mb-0">
            <h3 className="text-lg font-semibold mb-4">TechShop</h3>
            <p className="text-gray-400 max-w-xs">Hệ thống cung cấp sản phẩm công nghệ uy tín hàng đầu Việt Nam</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Liên hệ</h3>
            <p className="text-gray-400">Hotline: 1900 5301</p>
            <p className="text-gray-400">Email: support@techshop.vn</p>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 pt-6 text-sm text-gray-400 text-center">© 2025 TechShop</div>
      </footer>
    </div>
  );
};

export default App;