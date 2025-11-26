import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Chip,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import JiraIcon from '@mui/icons-material/IntegrationInstructions';
import TagIcon from '@mui/icons-material/Label';
import SentimentIcon from '@mui/icons-material/EmojiEmotions';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber';
import ticketService from '../services/ticketService';

const TicketDashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterTier, setFilterTier] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterPriority, setFilterPriority] = useState('All');

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const response = await ticketService.getTickets();
      if (response.success) {
        // Map backend data to frontend format
        const mappedTickets = response.data.map(t => ({
          id: t.id,
          title: t.subject,
          status: t.status,
          priority: t.priority || 'Medium', // Default if missing
          tier: t.tier || 'Tier 0',
          tags: t.ai_analysis?.tags || [],
          sentiment: t.ai_analysis?.sentiment || 'Neutral',
          sentimentScore: t.ai_analysis?.sentiment_score || 0.5,
          kbMatch: t.ai_analysis?.kb_match || 'No Match',
          slaRisk: t.ai_analysis?.sla_risk || false,
          createdAt: new Date(t.created_at).toLocaleString(),
        }));
        setTickets(mappedTickets);
        setError(null);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError('Failed to load tickets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredTickets = tickets.filter((ticket) => {
    if (filterTier !== 'All' && ticket.tier !== filterTier) return false;
    if (filterStatus !== 'All' && ticket.status !== filterStatus) return false;
    if (filterPriority !== 'All' && ticket.priority !== filterPriority) return false;
    return true;
  });

  const getPriorityColor = (priority) => {
    switch (priority?.toUpperCase()) {
      case 'CRITICAL':
        return '#D32F2F';
      case 'HIGH':
        return '#FF9500';
      case 'MEDIUM':
        return '#FBC02D';
      case 'LOW':
        return '#4A7C59';
      default:
        return '#999999';
    }
  };

  const getSentimentColor = (sentiment) => {
    const s = sentiment?.toLowerCase();
    if (s?.includes('frustrated') || s?.includes('negative')) return '#D32F2F';
    if (s?.includes('satisfied') || s?.includes('positive')) return '#4A7C59';
    return '#FF9500'; // Neutral
  };

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'OPEN':
        return '#FF9500';
      case 'IN_PROGRESS':
        return '#2196F3';
      case 'RESOLVED':
      case 'CLOSED':
        return '#4A7C59';
      default:
        return '#999999';
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, bgcolor: '#1a1a1a', minHeight: '100vh', width: '100%' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <ConfirmationNumberIcon sx={{ fontSize: 40, color: '#D4AF37' }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#D4AF37' }}>
              Help Desk Ticket Dashboard
            </Typography>
            <Typography variant="body1" sx={{ color: '#E0E0E0', mt: 0.5 }}>
              AI-enriched ticket management with auto-tagging, sentiment analysis, and KB recommendations
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Overall Tickets Statistics Section - Static for now, could be dynamic */}
      <Paper
        sx={{
          p: 3,
          mb: 4,
          backgroundColor: '#242424',
          border: '1px solid #333333',
          width: '100%',
        }}
      >
        <Typography variant="h3" sx={{ mb: 3, color: '#D4AF37', fontWeight: 'bold' }}>
          Overall Tickets Statistics
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, backgroundColor: '#1a1a1a', borderLeft: '4px solid #D4AF37' }}>
              <Typography variant="caption" sx={{ color: '#999999' }}>
                Total Tickets
              </Typography>
              <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                {tickets.length}
              </Typography>
            </Paper>
          </Grid>
          {/* Other stats kept static for demo purposes or need separate metrics API */}
        </Grid>
      </Paper>

      {/* Filters */}
      <Paper sx={{ p: 3, backgroundColor: '#242424', mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold' }}>
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#999999' }}>Tier</InputLabel>
              <Select
                value={filterTier}
                onChange={(e) => setFilterTier(e.target.value)}
                label="Tier"
                sx={{
                  backgroundColor: '#1a1a1a',
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333333' },
                }}
              >
                <MenuItem value="All">All Tiers</MenuItem>
                <MenuItem value="Tier 0">Tier 0</MenuItem>
                <MenuItem value="Tier 1">Tier 1</MenuItem>
                <MenuItem value="Tier 2">Tier 2</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#999999' }}>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
                sx={{
                  backgroundColor: '#1a1a1a',
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333333' },
                }}
              >
                <MenuItem value="All">All Statuses</MenuItem>
                <MenuItem value="OPEN">Open</MenuItem>
                <MenuItem value="IN_PROGRESS">In Progress</MenuItem>
                <MenuItem value="RESOLVED">Resolved</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#999999' }}>Priority</InputLabel>
              <Select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                label="Priority"
                sx={{
                  backgroundColor: '#1a1a1a',
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333333' },
                }}
              >
                <MenuItem value="All">All Priorities</MenuItem>
                <MenuItem value="CRITICAL">Critical</MenuItem>
                <MenuItem value="HIGH">High</MenuItem>
                <MenuItem value="MEDIUM">Medium</MenuItem>
                <MenuItem value="LOW">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Tickets Table */}
      <TableContainer component={Paper} sx={{ backgroundColor: '#242424' }}>
        {loading ? (
          <Box sx={{ p: 4, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress sx={{ color: '#D4AF37' }} />
          </Box>
        ) : error ? (
          <Box sx={{ p: 4 }}>
            <Alert severity="error">{error}</Alert>
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: '#1a1a1a' }}>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Ticket ID</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Title</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Priority</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Tier</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>AI Tags</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Sentiment</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>KB Match</TableCell>
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>SLA</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredTickets.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} sx={{ textAlign: 'center', color: '#999', py: 4 }}>
                    No tickets found
                  </TableCell>
                </TableRow>
              ) : (
                filteredTickets.map((ticket) => (
                  <TableRow
                    key={ticket.id}
                    sx={{
                      backgroundColor: '#242424',
                      '&:hover': { backgroundColor: '#2a2a2a' },
                      borderBottom: '1px solid #333333',
                    }}
                  >
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <JiraIcon sx={{ fontSize: '16px', color: '#0052CC' }} />
                        <Tooltip title={ticket.id}>
                          <Box
                            component="span"
                            onClick={() => {
                              navigator.clipboard?.writeText(ticket.id);
                            }}
                            sx={{
                              cursor: 'pointer',
                              textDecoration: 'underline',
                              '&:hover': {
                                color: '#FFD700',
                              },
                              maxWidth: '100px',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              display: 'inline-block',
                            }}
                          >
                            {ticket.id.substring(0, 8)}...
                          </Box>
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ color: '#ffffff', maxWidth: '200px' }}>
                      <Typography variant="body2">{ticket.title}</Typography>
                      <Typography variant="caption" sx={{ color: '#999999' }}>
                        {ticket.createdAt}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={ticket.priority}
                        size="small"
                        sx={{
                          backgroundColor: getPriorityColor(ticket.priority),
                          color: '#ffffff',
                          fontWeight: 'bold',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={ticket.status}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(ticket.status),
                          color: '#ffffff',
                          fontWeight: 'bold',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                        {ticket.tier}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {ticket.tags && ticket.tags.map((tag, idx) => (
                          <Chip
                            key={idx}
                            icon={<TagIcon />}
                            label={`${tag.label} (${tag.confidence}%)`}
                            size="small"
                            sx={{
                              backgroundColor: '#333333',
                              color: '#D4AF37',
                              fontSize: '11px',
                            }}
                          />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <SentimentIcon
                          sx={{
                            fontSize: '16px',
                            color: getSentimentColor(ticket.sentiment),
                          }}
                        />
                        <Typography variant="caption" sx={{ color: '#ffffff' }}>
                          {ticket.sentiment}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" sx={{ color: '#4A7C59' }}>
                        {ticket.kbMatch}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {ticket.slaRisk ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box
                            sx={{
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              backgroundColor: '#FF9500',
                            }}
                          />
                          <Typography variant="caption" sx={{ color: '#FF9500' }}>
                            At Risk
                          </Typography>
                        </Box>
                      ) : (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box
                            sx={{
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              backgroundColor: '#4A7C59',
                            }}
                          />
                          <Typography variant="caption" sx={{ color: '#4A7C59' }}>
                            OK
                          </Typography>
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </TableContainer>

      {/* Footer Note */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: '#242424', borderRadius: '8px', border: '1px solid #333333' }}>
        <Typography variant="caption" sx={{ color: '#999999' }}>
          <strong>AI-Enriched Data:</strong> Tags, sentiment, and KB recommendations are generated by the AI system. All confidence scores reflect model certainty. SLA risk is calculated based on ticket age and priority.
        </Typography>
      </Box>
    </Box>
  );
};

export default TicketDashboard;
