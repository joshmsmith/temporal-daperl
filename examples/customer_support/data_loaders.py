"""
Customer Support data loaders for the DAPER framework.
Provides specialized loaders for various customer support data sources.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_loaders import BaseDataLoader, DataLoaderRegistry, LoaderInfo


class TicketSystemLoader(BaseDataLoader):
    """Loader for ticketing system data (Zendesk, Salesforce Service Cloud, etc.)."""
    
    async def load_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load ticket data from ticketing system."""
        # In real implementation, this would connect to actual ticketing API
        data_file = config.get("data_file")
        ticket_statuses = config.get("ticket_statuses", ["open", "pending", "in-progress"])
        date_range = config.get("date_range", {})
        
        if data_file:
            # Load from file for example
            with open(data_file, 'r') as f:
                all_data = json.load(f)
                tickets = all_data.get("tickets", [])
        else:
            # Mock data for demonstration
            tickets = self._generate_mock_tickets()
        
        # Filter tickets based on status and date range
        filtered_tickets = []
        for ticket in tickets:
            if ticket_statuses and ticket.get("status") not in ticket_statuses:
                continue
                
            if self._ticket_in_date_range(ticket, date_range):
                filtered_tickets.append(ticket)
        
        self.logger.info(f"Loaded {len(filtered_tickets)} tickets from ticketing system")
        
        return {
            "tickets": filtered_tickets,
            "total_count": len(filtered_tickets),
            "filters_applied": {
                "statuses": ticket_statuses,
                "date_range": date_range
            },
            "loaded_at": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_tickets(self) -> List[Dict[str, Any]]:
        """Generate mock ticket data for testing."""
        return [
            {
                "id": "TICKET-001",
                "customer_id": "CUST-12345",
                "subject": "Cannot access SSO login",
                "description": "Getting error when trying to log in via SAML SSO",
                "status": "open",
                "priority": "high", 
                "created_at": "2024-12-26T08:00:00Z",
                "category": "authentication"
            },
            {
                "id": "TICKET-002", 
                "customer_id": "CUST-67890",
                "subject": "API rate limiting questions",
                "description": "What are the rate limits for Enterprise accounts?",
                "status": "in-progress",
                "priority": "normal",
                "created_at": "2024-12-26T09:15:00Z", 
                "category": "development"
            }
        ]
    
    def _ticket_in_date_range(self, ticket: Dict[str, Any], date_range: Dict[str, str]) -> bool:
        """Check if ticket falls within specified date range."""
        if not date_range:
            return True
            
        ticket_date = ticket.get("created_at", "")
        if not ticket_date:
            return True
            
        # Simple date comparison - in real implementation would parse dates properly
        start_date = date_range.get("start")
        end_date = date_range.get("end")
        
        if start_date and ticket_date < start_date:
            return False
        if end_date and ticket_date > end_date:
            return False
            
        return True
    
    def get_info(self) -> LoaderInfo:
        return LoaderInfo(
            name="ticket_system_loader",
            description="Load tickets from ticketing systems (Zendesk, Salesforce, etc.)",
            config_parameters=["data_file", "ticket_statuses", "date_range"],
            data_types=["tickets"],
            domain=self.domain,
            loader_class=TicketSystemLoader
        )


class CustomerDatabaseLoader(BaseDataLoader):
    """Loader for customer/CRM data."""
    
    async def load_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load customer data from CRM system."""
        data_file = config.get("data_file")
        customer_tiers = config.get("customer_tiers", [])
        include_inactive = config.get("include_inactive", False)
        
        if data_file:
            with open(data_file, 'r') as f:
                all_data = json.load(f)
                customers = all_data.get("customers", [])
        else:
            customers = self._generate_mock_customers()
        
        # Filter customers based on criteria
        filtered_customers = []
        for customer in customers:
            if customer_tiers and customer.get("account_type") not in customer_tiers:
                continue
                
            if not include_inactive and not customer.get("is_active", True):
                continue
                
            filtered_customers.append(customer)
        
        self.logger.info(f"Loaded {len(filtered_customers)} customers from CRM")
        
        return {
            "customers": filtered_customers,
            "total_count": len(filtered_customers),
            "filters_applied": {
                "tiers": customer_tiers,
                "include_inactive": include_inactive
            },
            "loaded_at": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_customers(self) -> List[Dict[str, Any]]:
        """Generate mock customer data for testing."""
        return [
            {
                "id": "CUST-12345",
                "name": "TechCorp Inc.",
                "email": "admin@techcorp.com",
                "account_type": "enterprise",
                "support_tier": "premium",
                "is_active": True,
                "health_score": 75,
                "satisfaction_score": 4.2
            },
            {
                "id": "CUST-67890", 
                "name": "StartupXYZ",
                "email": "founders@startupxyz.com",
                "account_type": "professional",
                "support_tier": "standard", 
                "is_active": True,
                "health_score": 85,
                "satisfaction_score": 4.8
            }
        ]
    
    def get_info(self) -> LoaderInfo:
        return LoaderInfo(
            name="customer_database_loader",
            description="Load customer data from CRM systems",
            config_parameters=["data_file", "customer_tiers", "include_inactive"],
            data_types=["customers"],
            domain=self.domain,
            loader_class=CustomerDatabaseLoader
        )


class ForumDataLoader(BaseDataLoader):
    """Loader for community forum data."""
    
    async def load_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load forum posts and discussions."""
        data_file = config.get("data_file")
        categories = config.get("categories", [])
        min_engagement = config.get("min_engagement", 0)
        
        if data_file:
            with open(data_file, 'r') as f:
                all_data = json.load(f)
                forum_posts = all_data.get("forum_posts", [])
        else:
            forum_posts = self._generate_mock_forum_posts()
        
        # Filter posts based on criteria
        filtered_posts = []
        for post in forum_posts:
            if categories and post.get("category") not in categories:
                continue
                
            engagement = post.get("upvotes", 0) + post.get("replies", 0)
            if engagement < min_engagement:
                continue
                
            filtered_posts.append(post)
        
        self.logger.info(f"Loaded {len(filtered_posts)} forum posts")
        
        return {
            "forum_posts": filtered_posts,
            "total_count": len(filtered_posts),
            "filters_applied": {
                "categories": categories,
                "min_engagement": min_engagement
            },
            "loaded_at": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_forum_posts(self) -> List[Dict[str, Any]]:
        """Generate mock forum post data for testing."""
        return [
            {
                "id": "POST-001",
                "title": "SSO Setup Issues with SAML",
                "content": "Having trouble configuring SAML SSO...",
                "category": "authentication",
                "author": "user123",
                "upvotes": 15,
                "replies": 8,
                "created_at": "2024-12-25T14:30:00Z"
            },
            {
                "id": "POST-002",
                "title": "API Rate Limit Best Practices", 
                "content": "What are the recommended patterns for handling rate limits?",
                "category": "development",
                "author": "dev_guru",
                "upvotes": 23,
                "replies": 12,
                "created_at": "2024-12-24T16:45:00Z"
            }
        ]
    
    def get_info(self) -> LoaderInfo:
        return LoaderInfo(
            name="forum_data_loader",
            description="Load community forum posts and discussions",
            config_parameters=["data_file", "categories", "min_engagement"],
            data_types=["forum_posts"],
            domain=self.domain,
            loader_class=ForumDataLoader
        )


class ProductDataLoader(BaseDataLoader):
    """Loader for product information and feature data."""
    
    async def load_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load product data and feature information."""
        data_file = config.get("data_file")
        product_types = config.get("product_types", [])
        include_deprecated = config.get("include_deprecated", False)
        
        if data_file:
            with open(data_file, 'r') as f:
                all_data = json.load(f)
                products = all_data.get("products", [])
        else:
            products = self._generate_mock_products()
        
        # Filter products based on criteria
        filtered_products = []
        for product in products:
            if product_types and product.get("type") not in product_types:
                continue
                
            if not include_deprecated and product.get("is_deprecated", False):
                continue
                
            filtered_products.append(product)
        
        self.logger.info(f"Loaded {len(filtered_products)} products")
        
        return {
            "products": filtered_products,
            "total_count": len(filtered_products),
            "filters_applied": {
                "types": product_types,
                "include_deprecated": include_deprecated
            },
            "loaded_at": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_products(self) -> List[Dict[str, Any]]:
        """Generate mock product data for testing."""
        return [
            {
                "id": "PROD-SSO",
                "name": "Single Sign-On (SSO)",
                "type": "security",
                "availability": ["enterprise"],
                "is_deprecated": False,
                "features": ["SAML 2.0", "LDAP", "Custom domains"]
            },
            {
                "id": "PROD-API",
                "name": "API Platform",
                "type": "integration", 
                "availability": ["professional", "enterprise"],
                "is_deprecated": False,
                "features": ["REST API", "GraphQL", "Webhooks", "Rate limiting"]
            }
        ]
    
    def get_info(self) -> LoaderInfo:
        return LoaderInfo(
            name="product_data_loader",
            description="Load product information and feature data",
            config_parameters=["data_file", "product_types", "include_deprecated"],
            data_types=["products"],
            domain=self.domain,
            loader_class=ProductDataLoader
        )


class KnowledgeBaseLoader(BaseDataLoader):
    """Loader for knowledge base articles and documentation."""
    
    async def load_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load knowledge base articles."""
        data_file = config.get("data_file")
        categories = config.get("categories", [])
        languages = config.get("languages", ["en"])
        
        if data_file:
            with open(data_file, 'r') as f:
                all_data = json.load(f)
                kb_articles = all_data.get("knowledge_base", [])
        else:
            kb_articles = self._generate_mock_kb_articles()
        
        # Filter articles based on criteria
        filtered_articles = []
        for article in kb_articles:
            if categories and article.get("category") not in categories:
                continue
                
            article_lang = article.get("language", "en")
            if article_lang not in languages:
                continue
                
            filtered_articles.append(article)
        
        self.logger.info(f"Loaded {len(filtered_articles)} knowledge base articles")
        
        return {
            "knowledge_base": filtered_articles,
            "total_count": len(filtered_articles),
            "filters_applied": {
                "categories": categories,
                "languages": languages
            },
            "loaded_at": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_kb_articles(self) -> List[Dict[str, Any]]:
        """Generate mock knowledge base articles for testing."""
        return [
            {
                "id": "KB-001",
                "title": "Setting up SAML Single Sign-On (SSO)",
                "category": "authentication",
                "language": "en",
                "content": "Complete guide for setting up SAML SSO...",
                "tags": ["sso", "saml", "authentication", "enterprise"]
            },
            {
                "id": "KB-002",
                "title": "Understanding API Rate Limits", 
                "category": "development",
                "language": "en",
                "content": "Comprehensive guide to API rate limits...",
                "tags": ["api", "rate-limits", "development", "integration"]
            }
        ]
    
    def get_info(self) -> LoaderInfo:
        return LoaderInfo(
            name="knowledge_base_loader", 
            description="Load knowledge base articles and documentation",
            config_parameters=["data_file", "categories", "languages"],
            data_types=["knowledge_base"],
            domain=self.domain,
            loader_class=KnowledgeBaseLoader
        )


class IntegratedSupportDataLoader(BaseDataLoader):
    """Composite loader that loads all customer support data sources."""
    
    async def load_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data from all customer support sources."""
        data_file = config.get("data_file", "data.json")
        
        # Load all data from the comprehensive data file
        try:
            with open(data_file, 'r') as f:
                all_data = json.load(f)
                
            self.logger.info(f"Loaded integrated customer support data from {data_file}")
            
            # Add metadata
            all_data["loaded_at"] = datetime.utcnow().isoformat()
            all_data["data_sources"] = {
                "tickets": len(all_data.get("tickets", [])),
                "customers": len(all_data.get("customers", [])),
                "forum_posts": len(all_data.get("forum_posts", [])),
                "products": len(all_data.get("products", [])),
                "knowledge_base": len(all_data.get("knowledge_base", []))
            }
            
            return all_data
            
        except FileNotFoundError:
            self.logger.warning(f"Data file {data_file} not found, generating mock data")
            return self._generate_integrated_mock_data()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing data file {data_file}: {e}")
            raise
    
    def _generate_integrated_mock_data(self) -> Dict[str, Any]:
        """Generate mock integrated data for all sources."""
        ticket_loader = TicketSystemLoader(self.domain)
        customer_loader = CustomerDatabaseLoader(self.domain)
        forum_loader = ForumDataLoader(self.domain)
        product_loader = ProductDataLoader(self.domain)
        kb_loader = KnowledgeBaseLoader(self.domain)
        
        return {
            "tickets": ticket_loader._generate_mock_tickets(),
            "customers": customer_loader._generate_mock_customers(),
            "forum_posts": forum_loader._generate_mock_forum_posts(),
            "products": product_loader._generate_mock_products(),
            "knowledge_base": kb_loader._generate_mock_kb_articles(),
            "loaded_at": datetime.utcnow().isoformat(),
            "data_source": "mock_generator"
        }
    
    def get_info(self) -> LoaderInfo:
        return LoaderInfo(
            name="integrated_support_data_loader",
            description="Load all customer support data sources in one operation",
            config_parameters=["data_file"],
            data_types=["tickets", "customers", "forum_posts", "products", "knowledge_base"],
            domain=self.domain,
            loader_class=IntegratedSupportDataLoader
        )


def register_customer_support_loaders(domain: str = "customer_support"):
    """Register customer support data loaders for a domain."""
    print(f"Registering customer support data loaders for domain: {domain}")
    
    loaders = [
        TicketSystemLoader,
        CustomerDatabaseLoader,
        ForumDataLoader,
        ProductDataLoader,
        KnowledgeBaseLoader,
        IntegratedSupportDataLoader
    ]
    
    for loader_class in loaders:
        DataLoaderRegistry.register_loader(loader_class, domain)
        print(f"  ✅ Registered: {loader_class.__name__}")
    
    print(f"Customer support data loaders registered successfully for {domain}!")


if __name__ == "__main__":
    # Register customer support loaders
    register_customer_support_loaders()
    
    # List registered loaders
    print("\nRegistered Customer Support Data Loaders:")
    for loader in DataLoaderRegistry.get_loaders_for_domain("customer_support"):
        print(f"  - {loader['name']}: {loader['description']}")