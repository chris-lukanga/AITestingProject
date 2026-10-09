"""Research preparation with observable progress and source-quality review."""
from services.taxonomy import SOURCES
from urllib.parse import urlsplit


class ResearchAgent:
    def __init__(self, notify):
        self.notify = notify

    def prepare(self, target, planner=None, cached=None):
        if cached is not None:
            evidence = dict(cached, reused=True)
            self.notify('Reusing retained research', 'The target context matches a saved research checkpoint.',
                        {'source_count': len(evidence.get('research', []))}, 'working')
        elif planner and planner.researcher:
            planner.on_research_event = self.notify
            evidence = planner.prepare_evidence(target)
            evidence['mode'] = 'Live public research'
        else:
            evidence = {'research': SOURCES, 'queries': [], 'mode': 'Bundled references', 'reused': False}
            self.notify('Reviewing bundled references', 'Public research credentials are unavailable or this run uses the local catalog.',
                        {'source_count': len(SOURCES)}, 'working')
        sources = evidence.get('research', [])
        https = sum(urlsplit(s.get('url', '')).scheme == 'https' for s in sources)
        evidence['review'] = {'source_count': len(sources), 'https_sources': https,
                              'queries': len(evidence.get('queries', [])),
                              'assessment': 'Sources available for planning' if sources else 'No sources returned; planning must disclose uncertainty'}
        self.notify('Research evidence reviewed', evidence['review']['assessment'], evidence['review'], 'completed')
        return evidence
