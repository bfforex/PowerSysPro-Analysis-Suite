/**
 * PwrSysPro Analysis Suite - Report Generator (Phase 4)
 * Generate professional PDF reports with all analysis results
 */

import React, { useState } from 'react';
import axios from 'axios';

const ReportGenerator = ({ projectId, currentProject }) => {
  const [generating, setGenerating] = useState(false);

  const generateReport = async () => {
    if (!projectId) {
      alert('No project selected');
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/generate-report`
      );

      if (response.data.status === 'success') {
        // Convert base64 to blob
        const binaryString = window.atob(response.data.pdf_data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'application/pdf' });

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.data.report_name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        alert(`âœ… Report generated successfully!\n\nFile: ${response.data.report_name}`);
      }
    } catch (error) {
      console.error('Report generation error:', error);
      alert(`âŒ Report generation failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <button
      onClick={generateReport}
      disabled={generating || !projectId}
      className="btn btn-success text-sm"
      title="Generate comprehensive PDF report"
    >
      {generating ? (
        <span className="flex items-center">
          <div className="spinner w-4 h-4 mr-2"></div>
          Generating...
        </span>
      ) : (
        'ðŸ“„ Generate Report'
      )}
    </button>
  );
};

export default ReportGenerator;
