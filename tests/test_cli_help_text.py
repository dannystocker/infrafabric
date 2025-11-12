"""
Unit tests for CLI help text module

Tests help text formatting, workflows, and quick reference.
"""

import pytest
from src.cli.help_text import (
    WITNESS_COMMANDS_HELP,
    COMMON_WORKFLOWS,
    QUICK_REFERENCE,
    format_command_help,
    format_workflow_help,
    format_quick_reference,
    get_command_epilog
)


class TestHelpTextData:
    """Test help text data structures"""

    def test_all_commands_have_help(self):
        """Test that all commands have help text"""
        expected_commands = ['log', 'query', 'verify', 'trace', 'cost', 'export']
        for cmd in expected_commands:
            assert cmd in WITNESS_COMMANDS_HELP
            assert 'short' in WITNESS_COMMANDS_HELP[cmd]
            assert 'long' in WITNESS_COMMANDS_HELP[cmd]

    def test_help_text_has_examples(self):
        """Test that help text includes examples"""
        for cmd, help_data in WITNESS_COMMANDS_HELP.items():
            assert 'examples' in help_data
            assert len(help_data['examples']) > 0
            for ex in help_data['examples']:
                assert 'description' in ex
                assert 'command' in ex

    def test_help_text_has_tips(self):
        """Test that help text includes tips"""
        for cmd, help_data in WITNESS_COMMANDS_HELP.items():
            assert 'tips' in help_data
            assert len(help_data['tips']) > 0

    def test_workflows_structure(self):
        """Test workflows data structure"""
        assert len(COMMON_WORKFLOWS) > 0
        for workflow in COMMON_WORKFLOWS:
            assert 'name' in workflow
            assert 'description' in workflow
            assert 'steps' in workflow
            assert len(workflow['steps']) > 0

    def test_quick_reference_structure(self):
        """Test quick reference data structure"""
        assert len(QUICK_REFERENCE) > 0
        for category, commands in QUICK_REFERENCE.items():
            assert isinstance(commands, dict)
            assert len(commands) > 0


class TestFormatCommandHelp:
    """Test command help formatting"""

    def test_format_log_help(self):
        """Test formatting help for log command"""
        help_text = format_command_help('log')
        assert '📖' in help_text  # Emoji indicator
        assert 'Create new witness entry' in help_text
        assert 'Examples:' in help_text
        assert 'Tips:' in help_text
        assert 'if witness log' in help_text

    def test_format_query_help(self):
        """Test formatting help for query command"""
        help_text = format_command_help('query')
        assert 'Search witness' in help_text
        assert '--component' in help_text
        assert '--trace-id' in help_text
        assert 'Examples:' in help_text

    def test_format_verify_help(self):
        """Test formatting help for verify command"""
        help_text = format_command_help('verify')
        assert 'hash chain' in help_text.lower()
        assert 'signature' in help_text.lower()
        assert 'Ed25519' in help_text

    def test_format_trace_help(self):
        """Test formatting help for trace command"""
        help_text = format_command_help('trace')
        assert 'trace' in help_text.lower()
        assert 'chronological' in help_text.lower()
        assert 'Examples:' in help_text

    def test_format_cost_help(self):
        """Test formatting help for cost command"""
        help_text = format_command_help('cost')
        assert 'token' in help_text.lower()
        assert 'cost' in help_text.lower()
        assert 'budget' in help_text.lower()

    def test_format_export_help(self):
        """Test formatting help for export command"""
        help_text = format_command_help('export')
        assert 'JSON' in help_text
        assert 'CSV' in help_text
        assert 'PDF' in help_text
        assert 'audit' in help_text.lower()

    def test_format_unknown_command(self):
        """Test formatting help for unknown command"""
        help_text = format_command_help('nonexistent')
        assert 'No enhanced help' in help_text
        assert 'nonexistent' in help_text

    def test_all_examples_have_commands(self):
        """Test that all examples include actual commands"""
        for cmd, help_data in WITNESS_COMMANDS_HELP.items():
            for ex in help_data['examples']:
                assert 'if witness' in ex['command'] or '#' in ex['command']


class TestFormatWorkflowHelp:
    """Test workflow help formatting"""

    def test_format_all_workflows(self):
        """Test formatting all workflows"""
        help_text = format_workflow_help()
        assert '🔧 Common Workflows' in help_text
        for workflow in COMMON_WORKFLOWS:
            assert workflow['name'] in help_text

    def test_format_specific_workflow(self):
        """Test formatting specific workflow"""
        workflow_name = COMMON_WORKFLOWS[0]['name']
        help_text = format_workflow_help(workflow_name)
        assert workflow_name in help_text
        assert COMMON_WORKFLOWS[0]['description'] in help_text

    def test_format_workflow_case_insensitive(self):
        """Test workflow lookup is case insensitive"""
        workflow_name = COMMON_WORKFLOWS[0]['name'].upper()
        help_text = format_workflow_help(workflow_name)
        assert help_text  # Should find workflow
        assert 'No workflow found' not in help_text

    def test_format_unknown_workflow(self):
        """Test formatting unknown workflow"""
        help_text = format_workflow_help('nonexistent workflow')
        assert 'No workflow found' in help_text

    def test_workflow_contains_steps(self):
        """Test that workflow help includes steps"""
        workflow_name = COMMON_WORKFLOWS[0]['name']
        help_text = format_workflow_help(workflow_name)
        # Should contain at least one step
        assert any(step in help_text for step in COMMON_WORKFLOWS[0]['steps'])


class TestFormatQuickReference:
    """Test quick reference formatting"""

    def test_format_quick_reference(self):
        """Test formatting quick reference"""
        help_text = format_quick_reference()
        assert '📋 Quick Reference' in help_text

    def test_quick_reference_has_categories(self):
        """Test quick reference includes all categories"""
        help_text = format_quick_reference()
        for category in QUICK_REFERENCE.keys():
            assert category in help_text

    def test_quick_reference_has_commands(self):
        """Test quick reference includes command examples"""
        help_text = format_quick_reference()
        assert 'if witness' in help_text
        assert '--component' in help_text
        assert '--format json' in help_text


class TestCommandEpilogs:
    """Test command epilog text"""

    def test_get_command_epilog(self):
        """Test getting epilog for commands"""
        epilog = get_command_epilog('log')
        assert '💡' in epilog
        assert 'See also' in epilog

    def test_epilog_references_related_commands(self):
        """Test epilogs reference related commands"""
        epilog = get_command_epilog('trace')
        assert 'query' in epilog or 'cost' in epilog

    def test_unknown_command_epilog(self):
        """Test epilog for unknown command"""
        epilog = get_command_epilog('nonexistent')
        assert epilog == ""  # Empty for unknown commands


class TestHelpTextContent:
    """Test help text content quality"""

    def test_examples_are_valid_commands(self):
        """Test that examples use valid command syntax"""
        for cmd, help_data in WITNESS_COMMANDS_HELP.items():
            for ex in help_data['examples']:
                cmd_text = ex['command']
                # Should contain the command name or be a comment
                assert f'if witness {cmd}' in cmd_text or cmd_text.strip().startswith('#')

    def test_tips_are_actionable(self):
        """Test that tips provide actionable guidance"""
        for cmd, help_data in WITNESS_COMMANDS_HELP.items():
            for tip in help_data['tips']:
                # Tips should be substantive (not just "use this command")
                assert len(tip) > 20
                # Should not be empty or just punctuation
                assert any(c.isalnum() for c in tip)

    def test_workflows_are_complete(self):
        """Test that workflows include complete examples"""
        for workflow in COMMON_WORKFLOWS:
            # Should have multiple steps
            assert len(workflow['steps']) >= 2
            # Should include at least one command
            steps_text = '\n'.join(workflow['steps'])
            assert 'if witness' in steps_text or '#' in steps_text

    def test_quick_reference_covers_main_use_cases(self):
        """Test quick reference covers main operations"""
        essential_operations = ['log', 'query', 'trace', 'verify']
        qr_text = str(QUICK_REFERENCE)
        for op in essential_operations:
            assert op in qr_text.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
