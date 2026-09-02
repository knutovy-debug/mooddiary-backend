import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import History from './History';
import Stats from './Stats';

const API_URL = import.meta.env.VITE_API_URL || "https://web-production-e70f0c.up.railway.app";

function App() {
  const { i18n } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [isLogin, setIsLogin] = useState(true);
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(localStorage.getItem('isSubscribed') === 'true');
  const [entriesToday, setEntriesToday] = useState(0);
  const [showQR, setShowQR] = useState(false);

  useEffect(() => {
    const fetchCount = async () => {
      if (!token) return;
      try {
        const response = await axios.get(`${API_URL}/api/v1/entries/today-count`, { headers: { Authorization: `Bearer ${token}` } });
        setEntriesToday(response.data.count);
        if (response.data.count >= 3 && !isSubscribed) setShowQR(true);
      } catch (err) { console.error(err); }
    };
    fetchCount();
  }, [token, isSubscribed]);

  const changeLanguage = (lng: string) => { i18n.changeLanguage(lng); };

  const handleLogin = async () => {
    setLoading(true); setError('');
    try {
      const url = isLogin ? '/auth/login' : '/auth/register';
      const response = await axios.post(`${API_URL}/api/v1${url}`, { email, password });
      localStorage.setItem('token', response.data.access_token);
      setToken(response.data.access_token);
    } catch (err: any) { setError(err.response?.data?.detail || "Ошибка авторизации"); }
    finally { setLoading(false); }
  };

  const handleSubmit = async () => {
    if (entriesToday >= 3 && !isSubscribed) { setShowQR(true); return; }
    setLoading(true); setError('');
    try {
      const response = await axios.post(`${API_URL}/api/v1/entries`, { text, lang: i18n.language }, { headers: { Authorization: `Bearer ${token}` } });
      setResult(response.data); setText(''); setEntriesToday(prev => prev + 1);
    } catch (err: any) { setError(err.response?.data?.detail || "Ошибка при отправке"); }
    finally { setLoading(false); }
  };

  const handlePaymentConfirmation = async () => {
    try { await axios.post(`${API_URL}/api/v1/entries/confirm-payment`, {}, { headers: { Authorization: `Bearer ${token}` } }); } catch (error) { console.error(error); }
    localStorage.setItem('isSubscribed', 'true'); setIsSubscribed(true); setShowQR(false);
    window.location.href = '/';
  };

  const logout = () => { localStorage.removeItem('token'); localStorage.removeItem('isSubscribed'); setToken(''); setIsSubscribed(false); window.location.href = '/'; };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-blue-50 to-indigo-100">
      <BrowserRouter>
        {/* Навигация */}
        <nav className="sticky top-0 z-10 bg-white/70 backdrop-blur-lg border-b border-white/40 shadow-sm">
          <div className="max-w-4xl mx-auto p-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🧠</span>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-600">MoodDiary</h1>
            </div>
            <div className="flex gap-2">
              <button onClick={() => changeLanguage('ru')} className="px-3 py-1 bg-white rounded-full shadow-sm text-sm">RU</button>
              <button onClick={() => changeLanguage('en')} className="px-3 py-1 bg-white rounded-full shadow-sm text-sm">EN</button>
              {token && (
                <button onClick={logout} className="px-3 py-1 bg-red-500 text-white rounded-full shadow-sm text-sm hover:bg-red-600">Выйти</button>
              )}
            </div>
          </div>
        </nav>

        <div className="max-w-4xl mx-auto p-6">
          {!token ? (
            // Экран входа
            <div className="mt-10 bg-white/60 backdrop-blur-lg border border-white/50 rounded-3xl shadow-xl p-8">
              <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">{isLogin ? 'С возвращением!' : 'Создать аккаунт'}</h2>
              {error && <p className="text-red-500 mb-4 text-center">⚠️ {error}</p>}
              <div className="space-y-4">
                <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} 
                  className="w-full bg-white/70 border border-gray-200 p-3 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500" />
                <input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} 
                  className="w-full bg-white/70 border border-gray-200 p-3 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500" />
                <button onClick={handleLogin} 
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white p-3 rounded-2xl font-bold shadow-lg hover:opacity-90 transition-opacity">
                  {loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
                </button>
                <p onClick={() => setIsLogin(!isLogin)} className="text-blue-600 cursor-pointer text-center mt-4 hover:underline">
                  {isLogin ? 'Нет аккаунта? Создать' : 'Уже есть аккаунт? Войти'}
                </p>
              </div>
            </div>
          ) : (
            // Дашборд
            <div>
              <div className="flex gap-4 mb-6">
                <Link to="/" className="flex-1 bg-white/60 backdrop-blur-lg rounded-2xl p-4 text-center font-semibold text-gray-700 shadow-sm hover:bg-white">📝 Запись</Link>
                <Link to="/history" className="flex-1 bg-white/60 backdrop-blur-lg rounded-2xl p-4 text-center font-semibold text-gray-700 shadow-sm hover:bg-white">📜 История</Link>
                <Link to="/stats" className="flex-1 bg-white/60 backdrop-blur-lg rounded-2xl p-4 text-center font-semibold text-gray-700 shadow-sm hover:bg-white">📊 Статистика</Link>
              </div>

              <Routes>
                <Route path="/" element={
                  <div>
                    {showQR && !isSubscribed && (
                      <div className="mt-6 bg-white/70 backdrop-blur-lg border border-white/50 rounded-3xl shadow-xl p-6 text-center">
                        <h3 className="text-xl font-bold mb-2">Лимит исчерпан</h3>
                        <p className="text-gray-600 mb-4">Вы использовали 3 бесплатные записи. Продолжайте с подпиской!</p>
                        <img src="/qr-code.png" alt="QR-код для оплаты" className="w-48 h-48 mx-auto mb-4 rounded-xl" />
                        <p className="text-lg font-bold text-purple-700">299 ₽ / месяц</p>
                        <button onClick={handlePaymentConfirmation} 
                          className="mt-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-8 py-3 rounded-full font-bold shadow-lg hover:opacity-90 transition-opacity">
                          ✅ Я оплатил
                        </button>
                      </div>
                    )}

                    {!showQR && (
                      <div className="mt-6 bg-white/70 backdrop-blur-lg border border-white/50 rounded-3xl shadow-xl p-6">
                        <h2 className="text-2xl font-bold mb-4 text-gray-800">Как прошёл твой день?</h2>
                        <textarea value={text} onChange={(e) => setText(e.target.value)} 
                          className="w-full bg-white border border-gray-200 p-4 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[150px]" 
                          placeholder="Напишите, что вы чувствуете..." />
                        <button onClick={handleSubmit} 
                          className="mt-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:opacity-90 transition-opacity">
                          Отправить на анализ ✨
                        </button>
                        
                        {result && (
                          <div className="mt-6 p-4 rounded-2xl bg-gradient-to-br from-green-50 to-blue-50 border border-green-200">
                            <p className="font-bold text-green-800">Настроение: {result.sentiment}</p>
                            <p className="text-gray-700 mt-2"><b>Совет:</b> {result.recommendation}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                } />
                <Route path="/history" element={<History />} />
                <Route path="/stats" element={<Stats />} />
              </Routes>
            </div>
          )}
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
