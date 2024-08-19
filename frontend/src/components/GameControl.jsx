/* eslint-disable react/prop-types */
// src/components/GameControl.jsx
import { FaPause, FaArrowDown } from 'react-icons/fa';
import * as XLSX from 'xlsx';


const GameControl = ({ timer, username, promptHistory }) => {

  const handleDownloadExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(promptHistory);
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

  return (
    <div className="w-full p-4 bg-gray-100 border border-gray-300 rounded-md">

       
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
            <div>{username}</div>
          </div>
        </div>
    </div>
  );
};

export default GameControl;
