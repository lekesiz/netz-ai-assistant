"""
AI Response Quality Tester for NETZ AI
Tests response quality, accuracy, and consistency
"""

import asyncio
import json
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import statistics
from dataclasses import dataclass, asdict
import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import ollama

console = Console()


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    prompt: str
    response: str
    response_time: float
    quality_score: float
    language_detected: str
    issues: List[str]
    passed: bool


@dataclass
class QualityMetrics:
    """Quality metrics for responses"""
    relevance_score: float
    completeness_score: float
    accuracy_score: float
    language_consistency: float
    response_time: float
    token_efficiency: float
    

class AIQualityTester:
    """Comprehensive AI quality testing"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.test_results: List[TestResult] = []
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def calculate_quality_score(self, prompt: str, response: str, response_time: float) -> Tuple[float, List[str]]:
        """Calculate quality score for a response"""
        issues = []
        scores = []
        
        # Response length check
        if len(response) < 10:
            issues.append("Response too short")
            scores.append(0.2)
        elif len(response) > 2000:
            issues.append("Response too verbose")
            scores.append(0.7)
        else:
            scores.append(1.0)
        
        # Response time check
        if response_time > 10:
            issues.append(f"Slow response: {response_time:.2f}s")
            scores.append(0.5)
        elif response_time > 5:
            scores.append(0.8)
        else:
            scores.append(1.0)
        
        # Check for errors or refusals
        error_phrases = ["error", "cannot", "unable to", "sorry", "can't"]
        if any(phrase in response.lower() for phrase in error_phrases):
            issues.append("Contains error or refusal phrases")
            scores.append(0.6)
        else:
            scores.append(1.0)
        
        # Language consistency check
        if "NETZ" in prompt and "NETZ" not in response:
            issues.append("Missing context about NETZ")
            scores.append(0.7)
        else:
            scores.append(1.0)
        
        # Calculate overall score
        quality_score = statistics.mean(scores)
        
        return quality_score, issues
    
    async def test_basic_queries(self):
        """Test basic query handling"""
        test_queries = [
            {
                "name": "Company Info",
                "prompt": "What is NETZ Informatique?",
                "expected_keywords": ["IT", "service", "informatique", "entreprise"],
                "language": "en"
            },
            {
                "name": "Services Query",
                "prompt": "Quels services propose NETZ Informatique?",
                "expected_keywords": ["dépannage", "formation", "maintenance", "informatique"],
                "language": "fr"
            },
            {
                "name": "Technical Support",
                "prompt": "Mon ordinateur ne démarre plus, que faire?",
                "expected_keywords": ["vérifier", "alimentation", "diagnostic", "technicien"],
                "language": "fr"
            },
            {
                "name": "Pricing Query",
                "prompt": "Combien coûte un dépannage informatique?",
                "expected_keywords": ["tarif", "devis", "prix", "intervention"],
                "language": "fr"
            },
            {
                "name": "QUALIOPI Query",
                "prompt": "Est-ce que NETZ est certifié QUALIOPI?",
                "expected_keywords": ["QUALIOPI", "certifié", "formation", "qualité"],
                "language": "fr"
            }
        ]
        
        console.print("[bold blue]Testing Basic Queries...[/bold blue]")
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                response = await self.client.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "messages": [{"role": "user", "content": query["prompt"]}],
                        "stream": False
                    }
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    # Check for expected keywords
                    found_keywords = [kw for kw in query["expected_keywords"] if kw.lower() in ai_response.lower()]
                    keyword_coverage = len(found_keywords) / len(query["expected_keywords"])
                    
                    quality_score, issues = self.calculate_quality_score(query["prompt"], ai_response, response_time)
                    
                    # Adjust score based on keyword coverage
                    quality_score = (quality_score + keyword_coverage) / 2
                    
                    if keyword_coverage < 0.5:
                        issues.append(f"Low keyword coverage: {keyword_coverage*100:.0f}%")
                    
                    test_result = TestResult(
                        test_name=query["name"],
                        prompt=query["prompt"],
                        response=ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                        response_time=response_time,
                        quality_score=quality_score,
                        language_detected=result.get("language", "unknown"),
                        issues=issues,
                        passed=quality_score >= 0.7
                    )
                    
                    self.test_results.append(test_result)
                    
                    status = "[green]PASS[/green]" if test_result.passed else "[red]FAIL[/red]"
                    console.print(f"  {status} {query['name']}: Score {quality_score:.2f}")
                    
                else:
                    console.print(f"  [red]FAIL[/red] {query['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                console.print(f"  [red]ERROR[/red] {query['name']}: {str(e)}")
    
    async def test_multilingual_support(self):
        """Test multilingual capabilities"""
        languages = [
            {"code": "fr", "prompt": "Bonjour, comment allez-vous?", "greeting": "bonjour"},
            {"code": "en", "prompt": "Hello, how can you help me?", "greeting": "hello"},
            {"code": "tr", "prompt": "Merhaba, NETZ nedir?", "greeting": "merhaba"},
            {"code": "de", "prompt": "Guten Tag, was ist NETZ?", "greeting": "guten"}
        ]
        
        console.print("\n[bold blue]Testing Multilingual Support...[/bold blue]")
        
        for lang in languages:
            try:
                response = await self.client.post(
                    f"{self.api_url}/api/chat",
                    json={"messages": [{"role": "user", "content": lang["prompt"]}]}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    detected_lang = result.get("language", "unknown")
                    
                    passed = detected_lang == lang["code"]
                    status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
                    console.print(f"  {status} {lang['code'].upper()}: Detected as {detected_lang}")
                    
            except Exception as e:
                console.print(f"  [red]ERROR[/red] {lang['code'].upper()}: {str(e)}")
    
    async def test_context_retention(self):
        """Test context retention across messages"""
        console.print("\n[bold blue]Testing Context Retention...[/bold blue]")
        
        conversation = [
            {"role": "user", "content": "Je m'appelle Pierre et j'ai un problème avec mon ordinateur."},
            {"role": "assistant", "content": ""},  # Will be filled
            {"role": "user", "content": "Il ne démarre plus depuis ce matin."},
            {"role": "assistant", "content": ""},  # Will be filled
            {"role": "user", "content": "Quel est mon prénom?"}
        ]
        
        messages = []
        
        for i, msg in enumerate(conversation):
            if msg["role"] == "user":
                messages.append(msg)
                
                response = await self.client.post(
                    f"{self.api_url}/api/chat",
                    json={"messages": messages}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    # Add assistant response to conversation
                    messages.append({"role": "assistant", "content": ai_response})
                    
                    # Check final response for context retention
                    if i == len(conversation) - 1:
                        if "Pierre" in ai_response:
                            console.print("  [green]PASS[/green] Context retained (name remembered)")
                        else:
                            console.print("  [red]FAIL[/red] Context lost (name not remembered)")
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        console.print("\n[bold blue]Testing Error Handling...[/bold blue]")
        
        edge_cases = [
            {"name": "Empty message", "messages": []},
            {"name": "Very long message", "messages": [{"role": "user", "content": "A" * 5000}]},
            {"name": "Special characters", "messages": [{"role": "user", "content": "Test €$¢ <script>alert('xss')</script>"}]},
            {"name": "Mixed languages", "messages": [{"role": "user", "content": "Bonjour, can you help με?"}]}
        ]
        
        for case in edge_cases:
            try:
                response = await self.client.post(
                    f"{self.api_url}/api/chat",
                    json={"messages": case["messages"]}
                )
                
                if response.status_code in [200, 422]:  # 422 for validation errors
                    console.print(f"  [green]PASS[/green] {case['name']}: Handled correctly")
                else:
                    console.print(f"  [yellow]WARN[/yellow] {case['name']}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                console.print(f"  [red]FAIL[/red] {case['name']}: {str(e)}")
    
    async def test_performance_benchmarks(self):
        """Test performance under various loads"""
        console.print("\n[bold blue]Testing Performance...[/bold blue]")
        
        # Single request benchmark
        single_times = []
        for i in range(5):
            start = time.time()
            response = await self.client.post(
                f"{self.api_url}/api/chat",
                json={"messages": [{"role": "user", "content": "Bonjour"}]}
            )
            if response.status_code == 200:
                single_times.append(time.time() - start)
        
        avg_single = statistics.mean(single_times) if single_times else 0
        console.print(f"  Average single request: {avg_single:.3f}s")
        
        # Concurrent requests benchmark
        async def make_request():
            start = time.time()
            response = await self.client.post(
                f"{self.api_url}/api/chat",
                json={"messages": [{"role": "user", "content": "Test concurrent"}]}
            )
            return time.time() - start if response.status_code == 200 else None
        
        # Test 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        concurrent_times = await asyncio.gather(*tasks)
        concurrent_times = [t for t in concurrent_times if t is not None]
        
        if concurrent_times:
            avg_concurrent = statistics.mean(concurrent_times)
            console.print(f"  Average concurrent request (10x): {avg_concurrent:.3f}s")
            
            if avg_concurrent < avg_single * 2:
                console.print("  [green]PASS[/green] Good concurrent performance")
            else:
                console.print("  [yellow]WARN[/yellow] Poor concurrent performance")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        
        avg_score = statistics.mean([r.quality_score for r in self.test_results]) if self.test_results else 0
        avg_response_time = statistics.mean([r.response_time for r in self.test_results]) if self.test_results else 0
        
        # Group issues
        all_issues = []
        for result in self.test_results:
            all_issues.extend(result.issues)
        
        issue_frequency = {}
        for issue in all_issues:
            issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_quality_score": avg_score,
                "average_response_time": avg_response_time
            },
            "common_issues": sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "test_results": [asdict(r) for r in self.test_results]
        }
        
        return report
    
    def display_summary(self):
        """Display test summary in a table"""
        table = Table(title="AI Quality Test Summary")
        table.add_column("Test", style="cyan", no_wrap=True)
        table.add_column("Score", justify="right")
        table.add_column("Time (s)", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Issues", style="yellow")
        
        for result in self.test_results:
            status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
            issues = ", ".join(result.issues[:2]) if result.issues else "[green]None[/green]"
            
            table.add_row(
                result.test_name,
                f"{result.quality_score:.2f}",
                f"{result.response_time:.2f}",
                status,
                issues
            )
        
        console.print(table)
        
        # Overall statistics
        report = self.generate_report()
        summary = report["summary"]
        
        console.print(f"\n[bold]Overall Results:[/bold]")
        console.print(f"  Success Rate: {summary['success_rate']:.1f}%")
        console.print(f"  Average Quality Score: {summary['average_quality_score']:.2f}/1.00")
        console.print(f"  Average Response Time: {summary['average_response_time']:.2f}s")
        
        if report["common_issues"]:
            console.print(f"\n[bold]Common Issues:[/bold]")
            for issue, count in report["common_issues"]:
                console.print(f"  - {issue}: {count} occurrences")


async def run_quality_tests():
    """Run all quality tests"""
    console.print("[bold green]Starting NETZ AI Quality Testing...[/bold green]\n")
    
    async with AIQualityTester() as tester:
        # Check if API is running
        try:
            response = await tester.client.get(f"{tester.api_url}/health")
            if response.status_code != 200:
                console.print("[red]API is not healthy. Please start the API first.[/red]")
                return
        except Exception:
            console.print("[red]Cannot connect to API. Please ensure it's running on http://localhost:8000[/red]")
            return
        
        # Run all test suites
        await tester.test_basic_queries()
        await tester.test_multilingual_support()
        await tester.test_context_retention()
        await tester.test_error_handling()
        await tester.test_performance_benchmarks()
        
        # Display results
        console.print("\n" + "="*50 + "\n")
        tester.display_summary()
        
        # Save report
        report = tester.generate_report()
        with open("ai_quality_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        console.print(f"\n[green]Report saved to ai_quality_report.json[/green]")


if __name__ == "__main__":
    asyncio.run(run_quality_tests())