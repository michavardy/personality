/* eslint-disable react/prop-types */
// src/components/GameControl.jsx
import { FaPause, FaArrowDown } from 'react-icons/fa';
import { useState } from 'react';
import * as XLSX from 'xlsx';


const GameControl = ({rules, currentScenario, scenarios, history, timer}) => {
    const [isRulesExpanded, setIsRulesExpanded] = useState(false);
    const [isScenarioExpanded, setIsScenarioExpanded] = useState(false);
      // Toggle function for expanding/collapsing
  
      const handleDownloadExcel = () => {
        const worksheet = XLSX.utils.json_to_sheet(history);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Transcript');
        const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'transcript.xlsx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      };

  const toggleRuleExpand = () => {
    setIsRulesExpanded(!isRulesExpanded);
  };
  const toggleScenarioExpand = () => {
    setIsScenarioExpanded(!isScenarioExpanded);
  };
  const handleRulesToggle = () => {
    setIsRulesExpanded((prev) => !prev);
  };
  const handleScenarioToggle = () => {
    setIsScenarioExpanded((prev) => !prev);
  };
const renderScenarioContent = () => {
        if (!isScenarioExpanded) {
            return (
              <p className="text-sm cursor-pointer" onClick={handleScenarioToggle}>
                Click to expand
              </p>
            );
          }
          return (
<div>
  {Object.keys(scenarios[currentScenario] || {}).length > 0 ? (
    Object.keys(scenarios[currentScenario]).map((key) => {
      const value = scenarios[currentScenario][key];
      return (
        <div key={key} className="mb-4">
          <strong className="block text-md mb-1">{key}:</strong>
          {Array.isArray(value) ? (
            <ul className="list-disc pl-4">
              {value.map((item, index) => (
                <li key={index} className="text-sm">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm">{value}</p>
          )}
        </div>
      );
    })
  ) : (
    <p>No Scenarios available</p>
  )}
</div>
          );
    }
const renderRulesContent = () => {
        if (!isRulesExpanded) {
            return (
              <p className="text-sm cursor-pointer" onClick={handleRulesToggle}>
                Click to expand
              </p>
            );
          }
          return (
            <div>
              {Object.keys(rules).length > 0 ? (
                Object.keys(rules).map((key) => (
                  <div key={key} className="mb-4">
                    <strong className="block text-md mb-1">{key}:</strong>
                    <ul className="list-disc pl-4">
                      {rules[key].map((item, index) => (
                        <li key={index} className="text-sm">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))
              ) : (
                <p>No rules available</p>
              )}
            </div>
          );
      };

  return (
    <div className="w-full p-4 bg-gray-100 border border-gray-300 rounded-md">
      {/*explination*/}
      <div className="flex flex-row">
      <div className="flex flex-col w-[90%] gap-2">
        {/* Rules */}
        <div className="text-left">
        <h3 className="text-sm font-medium cursor-pointer" onClick={toggleRuleExpand}>Rules: </h3>
        {renderRulesContent()}
        </div>

        {/* Current Scenario */}
        <div className="text-left flex flex-row">
          <h3 className="text-sm font-medium">Current Scenario:</h3>
          {currentScenario ? (<div className="text-xs  rounded px-2">{currentScenario}</div>) : (<></>)}
        </div>

        {/* Scenario Description */}
        <div className="text-left">
          <h3 className="text-sm font-medium cursor-pointer" onClick={toggleScenarioExpand}>Scenario Description</h3>
          {renderScenarioContent()}
        </div>
        </div>
        {/*Controls*/}
       <div className="flex flex-row justify-end items-start gap-2">
        {/* Time and Control Button */}
        <div className="flex items-center gap-2 p-2">
          <div className="text-sm font-medium">{timer}</div>
          <button className="p-1 bg-blue-500 text-white rounded-md hover:bg-blue-600">
            <FaPause />
          </button>
        </div>

        {/* Buttons */}
        <div className="flex gap-2 p-2">
          <button 
          className="p-1 bg-green-500 text-white rounded-md flex items-center hover:bg-green-600 text-sm"
          onClick={handleDownloadExcel}
          >
            <FaArrowDown className="mr-2" />
            Export
          </button>
        </div>
        </div>
      </div>
    </div>
  );
};

export default GameControl;
