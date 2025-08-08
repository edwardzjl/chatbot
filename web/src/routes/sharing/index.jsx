import "./index.css";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import CircularProgress from "@mui/material/CircularProgress";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import DeleteIcon from "@mui/icons-material/Delete";
import LaunchIcon from "@mui/icons-material/Launch";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import { useSnackbar } from "@/contexts/snackbar/hook";

const Sharing = () => {
    const [shares, setShares] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { setSnackbar } = useSnackbar();

    useEffect(() => {
        fetchShares();
    }, []);

    const fetchShares = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch("/api/shares");
            if (!response.ok) {
                throw new Error(`Failed to fetch shares: ${response.statusText}`);
            }
            const data = await response.json();
            setShares(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const deleteShare = async (shareId) => {
        try {
            const response = await fetch(`/api/shares/${shareId}`, {
                method: "DELETE",
            });
            if (response.ok) {
                setShares(shares.filter(share => share.id !== shareId));
                setSnackbar({
                    open: true,
                    message: "Share deleted successfully",
                    severity: "success",
                });
            } else {
                throw new Error(`Failed to delete share: ${response.statusText}`);
            }
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error deleting share: ${err.message}`,
                severity: "error",
            });
        }
    };

    const copyToClipboard = async (url) => {
        try {
            await navigator.clipboard.writeText(url);
            setSnackbar({
                open: true,
                message: "Share URL copied to clipboard",
                severity: "success",
            });
        } catch {
            setSnackbar({
                open: true,
                message: "Failed to copy URL",
                severity: "error",
            });
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box p={3}>
                <Alert severity="error">
                    Error loading shares: {error}
                </Alert>
            </Box>
        );
    }

    return (
        <Box p={3}>
            <Typography variant="h4" component="h1" gutterBottom>
                My Shares
            </Typography>
            
            {shares.length === 0 ? (
                <Box textAlign="center" py={6}>
                    <Typography variant="body1" color="text.secondary" gutterBottom>
                        You haven&apos;t shared any conversations yet.
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Share a conversation to see it listed here.
                    </Typography>
                </Box>
            ) : (
                <Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                        {shares.length} shared conversation{shares.length !== 1 ? 's' : ''}
                    </Typography>
                    
                    <Box display="flex" flexDirection="column" gap={2}>
                        {shares.map((share) => (
                            <Card key={share.id} variant="outlined">
                                <CardContent>
                                    <Typography variant="h6" component="h2" gutterBottom>
                                        {share.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Created: {formatDate(share.created_at)}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" noWrap>
                                        URL: {share.url}
                                    </Typography>
                                </CardContent>
                                <CardActions>
                                    <Button 
                                        size="small" 
                                        component={Link} 
                                        to={`/share/${share.id}`}
                                        startIcon={<LaunchIcon />}
                                    >
                                        View
                                    </Button>
                                    <Tooltip title="Copy share URL">
                                        <IconButton 
                                            size="small"
                                            onClick={() => copyToClipboard(share.url)}
                                        >
                                            <ContentCopyIcon />
                                        </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Delete share">
                                        <IconButton 
                                            size="small"
                                            color="error"
                                            onClick={() => deleteShare(share.id)}
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    </Tooltip>
                                </CardActions>
                            </Card>
                        ))}
                    </Box>
                </Box>
            )}
        </Box>
    );
};

export default Sharing;
