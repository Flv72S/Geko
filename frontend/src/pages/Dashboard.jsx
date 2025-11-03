import { motion } from 'framer-motion';
import { LayoutDashboard, TrendingUp, Users, FileText } from 'lucide-react';
import useAuthStore from '../store/authStore';

const Dashboard = () => {
  const { user } = useAuthStore();

  const stats = [
    {
      label: 'Progetti Attivi',
      value: '12',
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      label: 'Utenti',
      value: '45',
      icon: Users,
      color: 'bg-green-500',
    },
    {
      label: 'Crescita',
      value: '+23%',
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-6"
    >
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Benvenuto, {user?.username || 'Utente'}!
        </h1>
        <p className="text-gray-600">
          Ecco una panoramica della tua dashboard
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <LayoutDashboard className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Dashboard Geko AI Core</h2>
        </div>
        <p className="text-gray-600">
          Il sistema Geko AI Core è operativo e pronto per l'analisi dei dati.
          Utilizza la sidebar per navigare tra le diverse sezioni dell'applicazione.
        </p>
      </div>
    </motion.div>
  );
};

export default Dashboard;

