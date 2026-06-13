import React from 'react';

interface SurvivalBarsProps {
  health: number;
  energy: number;
  hunger: number;
  thirst: number;
}

export const SurvivalBars: React.FC<SurvivalBarsProps> = ({
  health,
  energy,
  hunger,
  thirst
}) => {
  const getBarColor = (value: number, type: 'hunger' | 'thirst'): string => {
    // For hunger and thirst: high values are bad (red), low values are good (green)
    if (type === 'hunger' || type === 'thirst') {
      if (value >= 70) return '#e74c3c'; // Red - critical
      if (value >= 40) return '#f39c12'; // Yellow - warning
      return '#27ae60'; // Green - good
    }
    // For health and energy: high values are good (green), low values are bad (red)
    if (value <= 30) return '#e74c3c'; // Red - critical
    if (value <= 60) return '#f39c12'; // Yellow - warning
    return '#27ae60'; // Green - good
  };

  const getBarLabel = (value: number, type: 'hunger' | 'thirst'): string => {
    if (type === 'hunger' || type === 'thirst') {
      if (value >= 70) return '⚠️';
      if (value >= 40) return '⚡';
      return '✓';
    }
    return '';
  };

  return (
    <div className="survival-bars">
      <div className="status-bar">
        <label>🍎 饥饿</label>
        <div className="bar">
          <div
            className="bar-fill"
            style={{
              width: `${hunger}%`,
              backgroundColor: getBarColor(hunger, 'hunger')
            }}
          />
        </div>
        <span className="bar-value">
          {hunger.toFixed(0)}% {getBarLabel(hunger, 'hunger')}
        </span>
      </div>

      <div className="status-bar">
        <label>💧 干渴</label>
        <div className="bar">
          <div
            className="bar-fill"
            style={{
              width: `${thirst}%`,
              backgroundColor: getBarColor(thirst, 'thirst')
            }}
          />
        </div>
        <span className="bar-value">
          {thirst.toFixed(0)}% {getBarLabel(thirst, 'thirst')}
        </span>
      </div>

      <div className="status-bar">
        <label>❤️ 健康</label>
        <div className="bar">
          <div
            className="bar-fill"
            style={{
              width: `${health}%`,
              backgroundColor: getBarColor(health, 'health')
            }}
          />
        </div>
        <span className="bar-value">{health.toFixed(0)}%</span>
      </div>

      <div className="status-bar">
        <label>⚡ 能量</label>
        <div className="bar">
          <div
            className="bar-fill"
            style={{
              width: `${energy}%`,
              backgroundColor: getBarColor(energy, 'energy')
            }}
          />
        </div>
        <span className="bar-value">{energy.toFixed(0)}%</span>
      </div>
    </div>
  );
};
