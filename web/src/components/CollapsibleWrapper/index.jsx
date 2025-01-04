import styles from './index.module.css';

import { useState } from 'react';
import PropTypes from 'prop-types';

const CollapsibleWrapper = ({
  children,
  initialCollapsed = false,
  duration = 300,
  collapsedWidth = '60px',
  expandedWidth = '250px',
  togglePosition = 'right', // 'left' or 'right'
  toggleLabel = { expand: '→', collapse: '←' },
  onToggle,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);

  const handleToggle = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    if (onToggle) onToggle(newState);
  };

  return (
    <div
      className={styles.collapsibleWrapper}
      style={{
        width: isCollapsed ? collapsedWidth : expandedWidth,
        transition: `width ${duration}ms ease`,
      }}
    >
      {togglePosition === 'left' && (
        <button className={styles.toggleButton} onClick={handleToggle}>
          {isCollapsed ? toggleLabel.expand : toggleLabel.collapse}
        </button>
      )}
      <div className={styles.collapsibleContent}>
        {children}
      </div>
      {togglePosition === 'right' && (
        <button className={styles.toggleButton} onClick={handleToggle}>
          {isCollapsed ? toggleLabel.expand : toggleLabel.collapse}
        </button>
      )}
    </div>
  );
};

CollapsibleWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  initialCollapsed: PropTypes.bool,
  duration: PropTypes.number,
  collapsedWidth: PropTypes.string,
  expandedWidth: PropTypes.string,
  togglePosition: PropTypes.oneOf(['left', 'right']),
  toggleLabel: PropTypes.shape({
    expand: PropTypes.string,
    collapse: PropTypes.string,
  }),
  onToggle: PropTypes.func,
};

export default CollapsibleWrapper;
