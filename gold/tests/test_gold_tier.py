"""
Gold Tier AI Employee - Test Suite

Tests for all core components.
"""

import pytest
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestFileSystemWatcher:
    """Tests for FileSystemWatcher"""
    
    def test_import(self):
        """Test that FileSystemWatcher can be imported"""
        from watchers.filesystem_watcher import FileSystemWatcher
        assert FileSystemWatcher is not None
    
    def test_initialization(self, tmp_path):
        """Test FileSystemWatcher initialization"""
        from watchers.filesystem_watcher import FileSystemWatcher
        
        vault = tmp_path / "vault"
        vault.mkdir()
        
        watcher = FileSystemWatcher(str(vault))
        assert watcher.vault_path == vault
        assert (vault / 'Needs_Action').exists()
    
    def test_generate_unique_id(self, tmp_path):
        """Test unique ID generation"""
        from watchers.filesystem_watcher import FileSystemWatcher
        import time
        
        vault = tmp_path / "vault"
        vault.mkdir()
        
        watcher = FileSystemWatcher(str(vault))
        id1 = watcher.generate_unique_id('TEST')
        time.sleep(1.1)  # Wait for timestamp to change
        id2 = watcher.generate_unique_id('TEST')
        
        assert id1.startswith('TEST_')
        assert id2.startswith('TEST_')


class TestGmailWatcher:
    """Tests for GmailWatcher"""
    
    def test_import(self):
        """Test that GmailWatcher can be imported"""
        from watchers.gmail_watcher import GmailWatcher
        assert GmailWatcher is not None
    
    def test_priority_determination(self, tmp_path):
        """Test email priority determination"""
        from watchers.gmail_watcher import GmailWatcher
        
        vault = tmp_path / "vault"
        vault.mkdir()
        
        watcher = GmailWatcher(
            str(vault),
            str(vault / 'creds.json'),
            str(vault / 'token.pickle')
        )
        
        # Test urgent keywords
        assert watcher._determine_priority('urgent meeting', 'test@example.com') == 'high'
        assert watcher._determine_priority('invoice request', 'test@example.com') == 'high'
        assert watcher._determine_priority('normal email', 'test@example.com') == 'normal'


class TestOdooClient:
    """Tests for OdooClient"""
    
    def test_import(self):
        """Test that OdooClient can be imported"""
        from services.odoo_client import OdooClient
        assert OdooClient is not None
    
    def test_initialization(self):
        """Test OdooClient initialization"""
        from services.odoo_client import OdooClient
        
        client = OdooClient(
            url='http://localhost:8069',
            db='test_db',
            username='admin',
            api_key='test_key'
        )
        
        assert client.url == 'http://localhost:8069'
        assert client.db == 'test_db'
        assert client.username == 'admin'


class TestMCPTools:
    """Tests for MCP tools"""
    
    def test_import_tools(self):
        """Test that MCP tools can be imported"""
        from mcp import tools
        assert hasattr(tools, 'send_email')
        assert hasattr(tools, 'post_linkedin')
        assert hasattr(tools, 'post_facebook')
        assert hasattr(tools, 'create_approval_request')
        assert hasattr(tools, 'check_approvals')
        assert hasattr(tools, 'update_dashboard')
        assert hasattr(tools, 'create_odoo_invoice')
        assert hasattr(tools, 'record_odoo_payment')
    
    def test_create_approval_request(self, tmp_path):
        """Test create_approval_request function"""
        from mcp.tools import create_approval_request
        import os
        
        # Save current dir
        old_cwd = os.getcwd()
        try:
            # Create test vault
            vault = tmp_path / "vault"
            vault.mkdir()
            (vault / 'Pending_Approval').mkdir()
            
            # Change to test directory
            os.chdir(tmp_path)
            
            # Create vault folder structure (avoid symlinks on Windows)
            test_vault = Path('./AI_Employee_Vault')
            if not test_vault.exists():
                test_vault.mkdir(parents=True, exist_ok=True)
                (test_vault / 'Pending_Approval').mkdir(exist_ok=True)
            
            # Temporarily copy test vault content
            import shutil
            for item in vault.iterdir():
                dest = test_vault / item.name
                if item.is_dir():
                    if not dest.exists():
                        shutil.copytree(item, dest)
            
            result = create_approval_request(
                action_type='test',
                details={'key': 'value'},
                reason='Testing',
            )
            assert result['status'] == 'created'
            assert 'approval_path' in result
            
        finally:
            os.chdir(old_cwd)
    
    def test_check_approvals(self, tmp_path):
        """Test check_approvals function"""
        from mcp.tools import check_approvals
        import os
        
        old_cwd = os.getcwd()
        try:
            vault = tmp_path / "vault"
            vault.mkdir()
            (vault / 'Pending_Approval').mkdir()
            
            os.chdir(tmp_path)
            
            # Create vault folder structure (avoid symlinks on Windows)
            test_vault = Path('./AI_Employee_Vault')
            if not test_vault.exists():
                test_vault.mkdir(parents=True, exist_ok=True)
                (test_vault / 'Pending_Approval').mkdir(exist_ok=True)
            
            result = check_approvals()
            assert result['status'] == 'success'
            assert 'pending_approvals' in result
            assert 'count' in result
            
        finally:
            os.chdir(old_cwd)


class TestScheduler:
    """Tests for TaskScheduler"""
    
    def test_import(self):
        """Test that TaskScheduler can be imported"""
        from scheduler.scheduler import TaskScheduler
        assert TaskScheduler is not None
    
    def test_initialization(self, tmp_path):
        """Test TaskScheduler initialization"""
        from scheduler.scheduler import TaskScheduler
        
        vault = tmp_path / "vault"
        vault.mkdir()
        
        scheduler = TaskScheduler(str(vault))
        assert scheduler.vault_path == vault
        assert scheduler.tasks == {}
    
    def test_add_task(self, tmp_path):
        """Test adding tasks to scheduler"""
        from scheduler.scheduler import TaskScheduler
        
        vault = tmp_path / "vault"
        vault.mkdir()
        
        scheduler = TaskScheduler(str(vault))
        scheduler.add_task(
            name='test_task',
            cron_expression='* * * * *',
            callback=lambda: None,
        )
        
        assert 'test_task' in scheduler.tasks
        assert scheduler.tasks['test_task'].name == 'test_task'


class TestScheduledTasks:
    """Tests for scheduled tasks"""
    
    def test_generate_daily_briefing(self, tmp_path):
        """Test daily briefing generation"""
        from scheduler.tasks import generate_daily_briefing
        
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / 'Done').mkdir()
        (vault / 'Pending_Approval').mkdir()
        (vault / 'Needs_Action').mkdir()
        
        result = generate_daily_briefing(str(vault))
        
        assert result['status'] == 'success'
        assert 'briefing_path' in result
        assert (vault / 'Briefings').exists()
    
    def test_generate_weekly_audit(self, tmp_path):
        """Test weekly audit generation"""
        from scheduler.tasks import generate_weekly_audit
        
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / 'Done').mkdir()
        
        result = generate_weekly_audit(str(vault))
        
        assert result['status'] == 'success'
        assert 'briefing_path' in result


class TestAuditLogger:
    """Tests for AuditLogger"""
    
    def test_import(self):
        """Test that AuditLogger can be imported"""
        from utils.audit_logger import AuditLogger
        assert AuditLogger is not None
    
    def test_logging(self, tmp_path):
        """Test audit logging"""
        from utils.audit_logger import AuditLogger
        
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / 'Logs').mkdir()
        
        logger = AuditLogger(str(vault))
        logger.log(
            action_type='test_action',
            actor='test_user',
            target='test_target',
            result='success',
        )
        
        # Verify log was created
        logs = logger.get_logs()
        assert len(logs) == 1
        assert logs[0]['action_type'] == 'test_action'


class TestRetryHandler:
    """Tests for retry handler"""
    
    def test_import(self):
        """Test that retry handler can be imported"""
        from utils.retry_handler import with_retry, TransientError
        assert with_retry is not None
        assert TransientError is not None
    
    def test_retry_decorator(self):
        """Test retry decorator"""
        from utils.retry_handler import with_retry, TransientError
        
        call_count = 0
        
        @with_retry(max_attempts=3, base_delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientError("Temporary error")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 3


class TestRalphWiggum:
    """Tests for Ralph Wiggum loop"""
    
    def test_import(self):
        """Test that RalphWiggumLoop can be imported"""
        from utils.ralph_wiggum import RalphWiggumLoop, ralph_loop
        assert RalphWiggumLoop is not None
        assert ralph_loop is not None
    
    def test_initialization(self, tmp_path):
        """Test RalphWiggumLoop initialization"""
        from utils.ralph_wiggum import RalphWiggumLoop
        
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / 'In_Progress').mkdir()
        (vault / 'Done').mkdir()
        
        loop = RalphWiggumLoop(
            prompt="Test task",
            vault_path=str(vault),
            max_iterations=5,
        )
        
        assert loop.prompt == "Test task"
        assert loop.max_iterations == 5
        assert loop.iteration == 0


class TestVaultStructure:
    """Tests for vault structure"""
    
    def test_required_folders_exist(self):
        """Test that required vault folders exist"""
        vault = Path(__file__).parent.parent / 'AI_Employee_Vault'
        
        required_folders = [
            'Inbox',
            'Needs_Action',
            'In_Progress',
            'Done',
            'Pending_Approval',
            'Approved',
            'Rejected',
            'Plans',
            'Briefings',
            'Logs',
            'Accounting',
            'Invoices',
            'Business_Goals',
            'Social_Media/LinkedIn',
            'Social_Media/Facebook',
            'Gmail',
            'Odoo',
            'Archive',
        ]
        
        for folder in required_folders:
            assert (vault / folder).exists(), f"Missing folder: {folder}"
    
    def test_required_files_exist(self):
        """Test that required vault files exist"""
        vault = Path(__file__).parent.parent / 'AI_Employee_Vault'
        
        required_files = [
            'Dashboard.md',
            'Company_Handbook.md',
            'Business_Goals/Company_Goals.md',
        ]
        
        for file in required_files:
            assert (vault / file).exists(), f"Missing file: {file}"


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow: watcher -> action file -> approval"""
        from watchers.filesystem_watcher import FileSystemWatcher
        from mcp.tools import create_approval_request
        import os
        import shutil
        
        # Setup
        vault = tmp_path / "vault"
        vault.mkdir()
        inbox = vault / 'Inbox'
        inbox.mkdir()
        (vault / 'Needs_Action').mkdir()
        
        # Initialize watcher
        watcher = FileSystemWatcher(str(vault))
        
        # Create test file
        test_file = inbox / 'test.txt'
        test_file.write_text('Test content')
        
        # Process file
        action_file = watcher.process_file(test_file)
        assert action_file is not None
        assert action_file.exists()
        
        # Create approval request
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Create vault structure (avoid symlinks on Windows)
            test_vault = Path('./AI_Employee_Vault')
            if not test_vault.exists():
                test_vault.mkdir(parents=True, exist_ok=True)
                (test_vault / 'Pending_Approval').mkdir(exist_ok=True)
            
            result = create_approval_request(
                action_type='test',
                details={'key': 'value'},
                reason='Testing',
            )
            assert result['status'] == 'created'
        finally:
            os.chdir(old_cwd)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
