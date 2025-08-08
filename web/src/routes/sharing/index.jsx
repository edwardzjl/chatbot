import "./index.css";

import { useState } from "react";
import { Link, useLoaderData } from "react-router-dom";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import DeleteIcon from "@mui/icons-material/Delete";
import LaunchIcon from "@mui/icons-material/Launch";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import { useSnackbar } from "@/contexts/snackbar/hook";
import { formatTimestamp } from "@/commons";

async function loader() {
    const response = await fetch("/api/shares");
    if (!response.ok) {
        throw new Error(`Failed to fetch shares: ${response.statusText}`);
    }
    const shares = await response.json();
    return { shares };
}

const Sharing = () => {
    const { shares: initialShares } = useLoaderData();
    const [shares, setShares] = useState(initialShares);
    const { setSnackbar } = useSnackbar();

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

    return (
        <div className="sharing-container">
            <Typography variant="h4" component="h1" gutterBottom>
                My Shares
            </Typography>
            
            {shares.length === 0 ? (
                <section className="empty-state">
                    <Typography variant="body1" color="text.secondary" gutterBottom>
                        You haven&apos;t shared any conversations yet.
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Share a conversation to see it listed here.
                    </Typography>
                </section>
            ) : (
                <div>
                    <Typography variant="body2" color="text.secondary" style={{ marginBottom: '1rem' }}>
                        {shares.length} shared conversation{shares.length !== 1 ? 's' : ''}
                    </Typography>
                    
                    <div className="shares-list">
                        {shares.map((share) => (
                            <Card key={share.id} variant="outlined" className="share-card">
                                <CardContent>
                                    <Typography variant="h6" component="h2" gutterBottom>
                                        {share.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Created: {formatTimestamp(share.created_at)}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" className="share-url">
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
                    </div>
                </div>
            )}
        </div>
    );
};

export default Sharing;
Sharing.loader = loader;
